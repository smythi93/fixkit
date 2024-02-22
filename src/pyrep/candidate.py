import os
from typing import List


class Candidate:
    def __init__(
        self, location, files: List[os.PathLike], gen: int = 0, fitness: float = 0.0
    ):
        self.location = location
        self.gen = gen
        self.fitness = fitness
        self.trees = {file: None for file in files}
