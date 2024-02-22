import ast
import os
from pathlib import Path
from typing import Optional

from pyrep.candidate import Candidate


class SearchError(RuntimeError):
    pass


class StatementFinder(ast.NodeVisitor):
    def __init__(self, src: os.PathLike, base: Optional[os.PathLike] = None):
        self.statements = []
        self.src = (Path(base or ".") / Path(src)).absolute()
        self.trees = dict()
        self.searched = False

    def build_candidate(self) -> Candidate:
        if self.searched:
            return Candidate(self.src, self.trees)
        else:
            raise SearchError("Source not searched")

    def search_source(self):
        if not self.searched:
            if self.src.is_file():
                self._search_file(self.src)
            elif self.src.is_dir():
                for directory, _, files in os.walk(self.src):
                    for file in files:
                        self._search_file(Path(directory, file).relative_to(self.src))

    def _search_file(self, file: Path):
        src = self.src / file
        if src.is_file() and src.suffix == ".py":
            with file.open("r") as f:
                source = f.read()
            tree = ast.parse(source)
            self.trees[file] = tree
            self.visit(tree)

    def visit_Expr(self, node):
        self.statements.append(node)

    def visit_Assign(self, node):
        self.statements.append(node)

    def visit_AugAssign(self, node):
        self.statements.append(node)

    def visit_AnnAssign(self, node):
        self.statements.append(node)

    def visit_Return(self, node):
        self.statements.append(node)

    def visit_Delete(self, node):
        self.statements.append(node)

    def visit_Raise(self, node):
        self.statements.append(node)

    def visit_Assert(self, node):
        self.statements.append(node)

    def visit_Global(self, node):
        self.statements.append(node)

    def visit_Nonlocal(self, node):
        self.statements.append(node)

    def visit_Pass(self, node):
        self.statements.append(node)

    def visit_Break(self, node):
        self.statements.append(node)

    def visit_Continue(self, node):
        self.statements.append(node)

    def visit_Import(self, node):
        self.statements.append(node)

    def visit_ImportFrom(self, node):
        self.statements.append(node)

    def visit_If(self, node):
        self.statements.append(node)
        self.generic_visit(node)

    def visit_For(self, node):
        self.statements.append(node)
        self.generic_visit(node)

    def visit_While(self, node):
        self.statements.append(node)
        self.generic_visit(node)

    def visit_With(self, node):
        self.statements.append(node)
        self.generic_visit(node)

    def visit_Try(self, node):
        self.statements.append(node)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.statements.append(node)
        self.generic_visit(node)
