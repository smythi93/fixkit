import ast
import os
from typing import Dict, Iterable


class Candidate:
    def __init__(
        self,
        src: os.PathLike,
        files: Iterable[os.PathLike] | Dict[os.PathLike, ast.AST],
        gen: int = 0,
        fitness: float = 0.0,
    ):
        self.src = src
        self.gen = gen
        self.fitness = fitness
        self.trees = (
            files if isinstance(files, Dict) else {file: None for file in files}
        )
