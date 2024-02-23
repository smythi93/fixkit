import ast
import os
from pathlib import Path
from typing import Optional

from pyrep.candidate import Candidate


class SearchError(RuntimeError):
    pass


class StatementFinder(ast.NodeVisitor):
    def __init__(self, src: os.PathLike, base: Optional[os.PathLike] = None):
        """
        Initializes the object with the given source path and optional base path.

        :param src: The source path
        :param base: Optional base path
        """
        self.identifier = 0
        self.statements = []
        self.src = (Path(base or ".") / Path(src)).absolute()
        self.trees = dict()
        self.searched = False

    def build_candidate(self) -> Candidate:
        """
        Build a candidate based on whether the source has been searched or not.

        :return Candidate: The candidate built from the source and trees if the source has been searched.
        :raises SearchError: If the source has not been searched.
        """
        if self.searched:
            return Candidate(self.src, self.trees)
        else:
            raise SearchError("Source not searched")

    def search_source(self):
        """
        Search the source for files or directories and call _search_file on each file found.
        """
        if not self.searched:
            if self.src.is_file():
                self._search_file(self.src)
            elif self.src.is_dir():
                for directory, _, files in os.walk(self.src):
                    for file in files:
                        self._search_file(Path(directory, file).relative_to(self.src))

    def _search_file(self, file: Path):
        """
        Search a file and parse its content using the given file path. Store the parsed tree in the trees dictionary.
        :param file: The file path to be searched and parsed
        :type file: Path
        :return: None
        """
        src = self.src / file
        if src.is_file() and src.suffix == ".py":
            with file.open("r") as f:
                source = f.read()
            tree = ast.parse(source)
            self.trees[file] = tree
            self.visit(tree)

    def generic_visit(self, node):
        """
        This function collects the statements and assigns an identifier to each statement.
        :param node: The node to be visited
        :return: None
        """
        if isinstance(node, ast.stmt):
            self.statements.append(node)
            node.identifier = self.next_identifier()
        return super().generic_visit(node)

    def next_identifier(self):
        """
        This function returns the next identifier.
        """
        identifier = self.identifier
        self.identifier += 1
        return identifier


class IdentifierRemover(ast.NodeVisitor):
    def generic_visit(self, node):
        if hasattr(node, "identifier"):
            delattr(node, "identifier")
        return super().generic_visit(node)
