import ast
from typing import Any, Collection

from pyrep.candidate import Candidate


class Repair:
    def select(self) -> Candidate:
        pass

    def mutate(self, selection: Candidate) -> Collection[Candidate]:
        pass

    def crossover(
        self, parent_1: Candidate, parent_2: Candidate
    ) -> Collection[Candidate]:
        pass
