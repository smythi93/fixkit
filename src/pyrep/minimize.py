import abc
from typing import List, Any

from pyrep.genetic.operators import MutationOperator


class Minimizer(abc.ABC):
    @abc.abstractmethod
    def minimize(self) -> Any:
        pass


class MutationMinimizer(Minimizer, abc.ABC):
    def __init__(self, mutations: List[MutationOperator]):
        self.mutations = mutations

    @abc.abstractmethod
    def minimize(self) -> List[MutationOperator]:
        return self.mutations


class DDMutationMinimizer(MutationMinimizer):
    def minimize(self) -> List[MutationOperator]:
        # TODO: implement DD search for minimal set of mutations
        return self.mutations
