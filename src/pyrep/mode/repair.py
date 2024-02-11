import ast
from typing import Any, Collection

Selection = Any
Mutant = ast.AST


class Repair:
    def select(self) -> Selection:
        pass

    def mutate(self, selection: Selection) -> Collection[Mutant]:
        pass

    def crossover(self) -> Collection[Mutant]:
        pass
