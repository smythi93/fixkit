import ast
import os
from typing import Dict, Iterable, Optional, List

from pyrep.genetic.operators import MutationOperator


class Candidate:
    def __init__(
        self,
        src: os.PathLike,
        trees: Iterable[os.PathLike] | Dict[os.PathLike, ast.AST] = None,
        files: Dict[int, os.PathLike] = None,
    ):
        """
        Initialize the class with the provided source path, generation number, fitness level, trees, and files.
        :param src (os.PathLike): The source path.
        :param gen (int, optional): The generation number. Defaults to 0.
        :param fitness (float, optional): The fitness level. Defaults to 0.0.
        :param trees (Iterable[os.PathLike] | Dict[os.PathLike, ast.AST], optional): Iterable of source paths or
        dictionary of source paths and AST objects. Defaults to None.
        :param files (Dict[int, os.PathLike], optional): Dictionary of file indices and source paths. Defaults to None.
        """
        self.src = src
        if trees:
            self.trees = (
                trees if isinstance(trees, Dict) else {file: None for file in trees}
            )
        else:
            self.trees = dict()
        self.files = files or dict()

    def clone(self):
        """
        Create a new Candidate object with the same properties as the current one.
        """
        return Candidate(self.src, self.trees, self.files)


class GeneticCandidate(Candidate):
    def __init__(
        self,
        src: os.PathLike,
        mutations: Optional[List[MutationOperator]] = None,
        gen: int = 0,
        fitness: float = 0.0,
        trees: Iterable[os.PathLike] | Dict[os.PathLike, ast.AST] = None,
        files: Dict[int, os.PathLike] = None,
    ):
        super().__init__(src, trees, files)
        self.mutations = mutations or list()
        self.gen = gen
        self.fitness = fitness

    @staticmethod
    def from_candidate(candidate: Candidate):
        return GeneticCandidate(
            candidate.src, trees=candidate.trees, files=candidate.files
        )

    def clone(self):
        """
        Create a new GeneticCandidate object with the same properties as the current one.
        """
        return GeneticCandidate(
            self.src, self.mutations, self.gen, self.fitness, self.trees, self.files
        )

    def __len__(self):
        """
        Return the length of the mutations list.
        """
        return len(self.mutations)

    def __getitem__(self, item):
        """
        Return the item at the given index in the mutations list.
        """
        return self.mutations[item]

    def __iter__(self):
        """
        Returns an iterator object that iterates over the mutations of the class instance.
        """
        return iter(self.mutations)
