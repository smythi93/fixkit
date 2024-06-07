"""
This module contains the StatementFinder class, which is used to search for statements in a given source file or
directory.
"""

import ast
import fnmatch
import os
from pathlib import Path
from typing import Dict, List, Optional

from fixkit.candidate import Candidate


class SearchError(RuntimeError):
    """
    Error raised when the source has not been searched.
    """

    pass


class StatementFinder(ast.NodeVisitor):
    def __init__(
        self,
        src: os.PathLike,
        excludes: Optional[List[str]] = None,
        line_mode: bool = False,
    ):
        """
        Initialize the StatementFinder with the given source path and optional excludes.
        :param os.PathLike src: The source path to search.
        :param Optional[List[str]] excludes: The list of patterns to exclude from the search.
        """
        self.identifier = 0
        self.statements: Dict[int, ast.AST] = dict()
        self.lines: Dict[str, Dict[int, List[int]]] = dict()
        self.src = Path(src)
        self.trees = dict()
        self.files = dict()
        self.searched = False
        self.current_file = None
        self.excludes = excludes or list()
        self.line_mode = line_mode

    def build_candidate(self) -> Candidate:
        """
        Build a candidate from the search results.
        :return Candidate: The candidate built from the search results.
        """
        if self.searched:
            return Candidate(
                self.src,
                statements=self.statements,
                trees=self.trees,
                files=self.files,
                lines=self.lines,
            )
        else:
            raise SearchError("Source not searched")

    def search_source(self):
        """
        Search the source for files or directories and call _search_file on each file found.
        """
        if not self.searched:
            if self.src.is_file():
                self._search_file(".")
            elif self.src.is_dir():
                for directory, _, files in os.walk(self.src):
                    if not any(fnmatch.fnmatch(directory, e) for e in self.excludes):
                        for file in files:
                            self._search_file(
                                str(Path(directory, file).relative_to(self.src))
                            )
            self.searched = True

    def _search_file(self, file: str):
        """
        Search a file and parse its content using the given file path. Store the parsed tree in the trees' dictionary.
        :param str file: The file path to be searched and parsed.
        """
        src = self.src / file
        if (
            src.is_file()
            and src.suffix == ".py"
            and not any(fnmatch.fnmatch(file, e) for e in self.excludes)
        ):
            with src.open("r") as f:
                source = f.read()
            tree = ast.parse(source)
            self.trees[file] = tree
            self.current_file = file
            self.visit(tree)

    def check(self, node: ast.AST):
        """
        This function checks if the node is a statement.
        :param ast.AST node: The node to be checked.
        """
        if self.line_mode:
            return isinstance(node, ast.stmt) and not hasattr(node, "body")
        else:
            return isinstance(node, ast.stmt)

    def generic_visit(self, node: ast.AST):
        """
        This function collects the statements and assigns an identifier to each statement.
        :param ast.AST node: The node to be visited.
        """
        if self.check(node):
            identifier = self.next_identifier()
            self.statements[identifier] = node
            self.files[identifier] = self.current_file
            if self.current_file not in self.lines:
                self.lines[self.current_file] = dict()
            if node.lineno not in self.lines[self.current_file]:
                self.lines[self.current_file][node.lineno] = list()
            self.lines[self.current_file][node.lineno].append(identifier)
        return super().generic_visit(node)

    def next_identifier(self) -> int:
        """
        This function returns the next identifier.
        :return int: The next identifier.
        """
        identifier = self.identifier
        self.identifier += 1
        return identifier


__all__ = ["StatementFinder", "SearchError"]
