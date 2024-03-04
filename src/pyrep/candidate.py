import ast
import os
from typing import Dict, Iterable, Optional, List

from pyrep.genetic.operators import MutationOperator


class Candidate:
    def __init__(
        self,
        src: os.PathLike,
        statements: Dict[int, ast.AST] = None,
        trees: Iterable[os.PathLike] | Dict[os.PathLike, ast.AST] = None,
        files: Dict[int, os.PathLike] = None,
        lines: Dict[str, Dict[int, List[int]]] = None,
    ):
        """
        Initialize the class with the provided source path, statements, trees, files, and lines.
        :param src (os.PathLike): The source path.
        :param statements (Dict[int, ast.AST], optional): Dictionary of statement indices and AST objects.
        Defaults to None.
        :param trees (Iterable[os.PathLike] | Dict[os.PathLike, ast.AST], optional): Iterable of source paths or
        dictionary of source paths and AST objects. Defaults to None.
        :param files (Dict[int, os.PathLike], optional): Dictionary of file indices and source paths. Defaults to None.
        :param lines (Dict[str, Dict[int, List[int]]], optional): Dictionary of source paths and line numbers to
        statement identifiers. Defaults to None.
        """
        self.src = src
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
        """
        return Candidate(self.src, self.trees, self.files, self.lines)


class GeneticCandidate(Candidate):
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
        Initialize the class with the provided source path, generation number, fitness level, trees, and files.
        :param src (os.PathLike): The source path.
        :param mutations (List[MutationOperator], optional): List of mutation operators. Defaults to None.
        :param gen (int, optional): Generation number. Defaults to 0.
        :param fitness (float, optional): Fitness level. Defaults to 0.0.
        :param statements (Dict[int, ast.AST], optional): Dictionary of statement indices and AST objects.
        Defaults to None.
        :param trees (Iterable[os.PathLike] | Dict[os.PathLike, ast.AST], optional): Iterable of source paths or
        dictionary of source paths and AST objects. Defaults to None.
        :param files (Dict[int, os.PathLike], optional): Dictionary of file indices and source paths. Defaults to None.
        :param lines (Dict[str, Dict[int, List[int]]], optional): Dictionary of source paths and line numbers to
        statement identifiers. Defaults to None.
        """
        super().__init__(src, statements, trees, files, lines)
        self.mutations = mutations or list()
        self.gen = gen
        self.fitness = fitness

    @staticmethod
    def from_candidate(candidate: Candidate) -> "GeneticCandidate":
        """
        Create a new GeneticCandidate object with the same properties as the given Candidate object.
        :param candidate (Candidate): The Candidate object to copy.
        :return GeneticCandidate: The new GeneticCandidate object.
        """
        return GeneticCandidate(
            candidate.src,
            statements=candidate.statements,
            trees=candidate.trees,
            files=candidate.files,
            lines=candidate.lines,
        )

    def clone(self) -> "GeneticCandidate":
        """
        Create a new GeneticCandidate object with the same properties as the current one.
        """
        return GeneticCandidate(
            self.src,
            self.mutations,
            self.gen,
            self.fitness,
            self.trees,
            self.files,
            self.lines,
        )

    def __len__(self) -> int:
        """
        Return the length of the mutations list.
        """
        return len(self.mutations)

    def __getitem__(self, item) -> MutationOperator | List[MutationOperator]:
        """
        Return the item at the given index in the mutations list.
        """
        return self.mutations[item]

    def __iter__(self) -> Iterable[MutationOperator]:
        """
        Returns an iterator object that iterates over the mutations of the class instance.
        """
        return iter(self.mutations)

    def offspring(self, mutations: List[MutationOperator]):
        """
        Create a new GeneticCandidate object with the given mutations and generation number.
        :param mutations (List[MutationOperator]): List of mutation operators.
        """
        candidate = self.clone()
        candidate.mutations = mutations
        candidate.gen = self.gen + 1
        return candidate
