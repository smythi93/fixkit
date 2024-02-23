import ast
import os
from typing import Dict, Iterable, Optional, List

from pyrep.genetic.operators import MutationOperator


class Candidate:
    TREES: Dict[os.PathLike, ast.AST] = dict()

    def __init__(
        self,
        src: os.PathLike,
        files: Iterable[os.PathLike] | Dict[os.PathLike, ast.AST] = None,
        mutations: Optional[List[MutationOperator]] = None,
        gen: int = 0,
        fitness: float = 0.0,
    ):
        """
        Initializes the class with the provided source path, optional files, generation number, and fitness value.
        :param src: The source path (os.PathLike)
        :param files: Optional files as an Iterable[os.PathLike] or Dict[os.PathLike, ast.AST]
        :param mutations: Optional mutations as a List[MutationOperator]
        :param gen: Generation number (int)
        :param fitness: Fitness value (float)
        """
        self.src = src
        self.gen = gen
        self.fitness = fitness
        self.mutations = mutations or list()
        if files:
            self.TREES = (
                files if isinstance(files, Dict) else {file: None for file in files}
            )
