"""
The candidate module provides the necessary tools to represent a candidate for repair.
"""

import ast
import os
from pathlib import Path
from typing import Dict, Iterable, Optional, List

from pyrep.genetic.operators import MutationOperator


class Candidate:
    """
    Class for representing a candidate for repair.
    """

    def __init__(
        self,
        src: os.PathLike,
        statements: Optional[Dict[int, ast.AST]] = None,
        trees: Optional[Iterable[os.PathLike] | Dict[os.PathLike, ast.AST]] = None,
        files: Optional[Dict[int, os.PathLike]] = None,
        lines: Optional[Dict[str, Dict[int, List[int]]]] = None,
    ):
        """
        Initialize the class with the provided source path, statements, trees, files, and lines.
        :param os.PathLike src: The source path.
        :param Optional[Dict[int, ast.AST]] statements: Dictionary of statement indices and AST objects.
        :param Optional[Iterable[os.PathLike] | Dict[os.PathLike, ast.AST]] trees: Iterable of source paths or
        dictionary of source paths and AST objects.
        :param Optional[Dict[int, os.PathLike]] files: Dictionary of file indices and source paths.
        :param Optional[Dict[str, Dict[int, List[int]]]] lines: Dictionary of source paths and line numbers to
        statement identifiers.
        """
        self.src: Path = Path(src)
        self.statements = statements or dict()
        if trees:
            self.trees = (
                trees if isinstance(trees, Dict) else {file: None for file in trees}
            )
        else:
            self.trees = dict()
        self.files = files or dict()
        self.lines = lines or dict()

    def clone(self) -> "Candidate":
        """
        Create a new Candidate object with the same properties as the current one.
        :return Candidate: The new Candidate object.
        """
        return Candidate(self.src, self.statements, self.trees, self.files, self.lines)

    def __repr__(self) -> str:
        """
        Return the string representation of the class instance.
        :return str: The string representation of the class instance.
        """
        return f"Candidate@{self.src}"

    def __hash__(self) -> int:
        """
        Return the hash of the source path.
        :return int: The hash of the source path.
        """
        return hash(self.src)

    def __eq__(self, other) -> bool:
        """
        Return True if the source paths are equal, False otherwise.
        :param other: The other object to compare.
        :return bool: True if the source paths are equal, False otherwise.
        """
        return hasattr(other, "src") and self.src == other.src


class GeneticCandidate(Candidate):
    """
    Class for representing a genetic candidate for repair.
    """

    def __init__(
        self,
        src: os.PathLike,
        mutations: Optional[List[MutationOperator]] = None,
        gen: int = 0,
        fitness: float = 0.0,
        statements: Dict[int, ast.AST] = None,
        trees: Iterable[os.PathLike] | Dict[os.PathLike, ast.AST] = None,
        files: Dict[int, os.PathLike] = None,
        lines: Dict[os.PathLike, Dict[int, List[int]]] = None,
    ):
        """
        Initialize the class with the provided source path, mutations, generation number, fitness, statements, trees,
        files, and lines.
        :param os.PathLike src: The source path.
        :param Optional[List[MutationOperator]] mutations: List of mutation operators.
        :param int gen: The generation number.
        :param float fitness: The fitness of the candidate.
        :param Dict[int, ast.AST] statements: Dictionary of statement indices and AST objects.
        :param Optional[Iterable[os.PathLike] | Dict[os.PathLike, ast.AST]] trees: Iterable of source paths or
        dictionary of source paths and AST objects.
        :param Optional[Dict[int, os.PathLike]] files: Dictionary of file indices and source paths.
        :param Optional[Dict[os.PathLike, Dict[int, List[int]]]] lines: Dictionary of source paths and line numbers to
        statement identifiers.
        """
        super().__init__(src, statements, trees, files, lines)
        self.mutations = mutations or list()
        self.gen = gen
        self.fitness = fitness

    @staticmethod
    def from_candidate(candidate: Candidate) -> "GeneticCandidate":
        """
        Create a new GeneticCandidate object with the same properties as the given Candidate object.
        :param Candidate candidate: The Candidate object to create the GeneticCandidate from.
        :return GeneticCandidate: The new GeneticCandidate object.
        """
        return GeneticCandidate(
            candidate.src,
            statements=candidate.statements,
            trees=candidate.trees,
            files=candidate.files,
            lines=candidate.lines,
        )

    def clone(self, change_gen: Optional[bool] = True) -> "GeneticCandidate":
        """
        Create a new GeneticCandidate object with the same properties as the current one.
        :param Optional[bool] change_gen: Whether to change the generation number. Defaults to True.
        :return GeneticCandidate: The new GeneticCandidate object.
        """
        return GeneticCandidate(
            src=self.src,
            mutations=self.mutations,
            gen=self.gen + 1 if change_gen else self.gen,
            fitness=self.fitness,
            statements=self.statements,
            trees=self.trees,
            files=self.files,
            lines=self.lines,
        )

    def __len__(self) -> int:
        """
        Return the length of the mutations list.
        :return int: The length of the mutations list.
        """
        return len(self.mutations)

    def __getitem__(self, item) -> MutationOperator | List[MutationOperator]:
        """
        Return the item at the given index in the mutations list.
        :param item: The index of the item to return.
        :return MutationOperator | List[MutationOperator]: The item at the given index in the mutations list.
        """
        return self.mutations[item]

    def __iter__(self) -> Iterable[MutationOperator]:
        """
        Returns an iterator object that iterates over the mutations of the class instance.
        :return Iterable[MutationOperator]: An iterator object that iterates over the mutations of the class instance.
        """
        return iter(self.mutations)

    def offspring(
        self, mutations: List[MutationOperator], change_gen: bool = True
    ) -> "GeneticCandidate":
        """
        Create a new GeneticCandidate object with the given mutations and generation number.
        :param List[MutationOperator] mutations: The mutations to add to the new GeneticCandidate object.
        :param bool change_gen: Whether to change the generation number. Defaults to True.
        :return GeneticCandidate: The new GeneticCandidate object.
        """
        candidate = self.clone(change_gen=change_gen)
        candidate.mutations = mutations
        return candidate

    def __repr__(self) -> str:
        """
        Return the string representation of the class instance.
        :return str: The string representation of the class instance.
        """
        return f"GeneticCandidate@{self.src}({self.gen})[{self.fitness:.2f}]"

    def __hash__(self) -> int:
        """
        Return the hash of the source path.
        :return int: The hash of the source path.
        """
        return hash(tuple(self.mutations))

    def __eq__(self, other) -> bool:
        """
        Return True if the source paths and mutations are equal, False otherwise.
        :param other: The other object to compare.
        :return bool: True if the source paths and mutations are equal, False otherwise.
        """
        return (
            hasattr(other, "src")
            and hasattr(other, "mutations")
            and self.src == other.src
            and self.mutations == other.mutations
        )


__all__ = ["Candidate", "GeneticCandidate"]
