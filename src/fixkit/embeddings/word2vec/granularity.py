import abc
import ast
import enum
import fnmatch
import os
from pathlib import Path
from typing import Optional, List


class Granularity(enum.Enum):
    FILE = "FILE"
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"


class CorpusBuilder(ast.NodeVisitor):
    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        terminals = list()
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        terminals += self.visit(item)
            elif isinstance(value, ast.AST):
                terminals += self.visit(value)
            elif field in ["name", "id", "arg", "attr"] and isinstance(value, str):
                terminals.append(value)
        return terminals

    def visit_Constant(self, node):
        return [f"<{type(node.value).__name__.upper()}>"]


class GranularityVisitor(abc.ABC, ast.NodeVisitor):
    def __init__(self):
        self.builder = CorpusBuilder()

    def generic_visit(self, node):
        terminals = list()
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        terminals += self.visit(item)
            elif isinstance(value, ast.AST):
                terminals += self.visit(value)
        return terminals


class FileVisitor(GranularityVisitor):
    def visit_Module(self, node):
        return [self.builder.visit(node)]


class ClassVisitor(GranularityVisitor):
    def visit_ClassDef(self, node):
        return [self.builder.visit(node)]


class FunctionVisitor(GranularityVisitor):
    def visit_FunctionDef(self, node):
        return [self.builder.visit(node)]

    def visit_AsyncFunctionDef(self, node):
        return [self.builder.visit(node)]


GRANULARITY_MAPPING = {
    Granularity.FILE: FileVisitor,
    Granularity.CLASS: ClassVisitor,
    Granularity.FUNCTION: FunctionVisitor,
}


class GranularityBuilder:
    def __init__(
        self,
        src: os.PathLike,
        granularity: Granularity,
        excludes: Optional[List[str]] = None,
    ):
        self.src = Path(src)
        self.excludes = excludes or list()
        self.visitor = GRANULARITY_MAPPING[granularity]()

    def build(self) -> List[List[str]]:
        terminals = list()
        if self.src.is_file():
            terminals += self.build_from_file("")
        elif self.src.is_dir():
            for directory, _, files in os.walk(self.src):
                if not any(fnmatch.fnmatch(directory, e) for e in self.excludes):
                    for file in files:
                        terminals += self.build_from_file(
                            str(Path(directory, file).relative_to(self.src))
                        )
        return terminals

    def visit(self, node: ast.AST):
        return self.visitor.visit(node)

    def build_from_file(self, file: str) -> List[List[str]]:
        src = self.src / file
        if (
            src.is_file()
            and src.suffix == ".py"
            and not any(fnmatch.fnmatch(file, e) for e in self.excludes)
        ):
            with src.open("r") as f:
                source = f.read()
            tree = ast.parse(source)
            return self.visit(tree)
        return []
