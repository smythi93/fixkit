import abc
from typing import Collection, List

from pyrep.candidate import Candidate
from pyrep.localization import Localization, WeightedLocation


class Repair(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def repair(self):
        pass


class LocalizationRepair(Repair, abc.ABC):
    def __init__(self, localization: Localization):
        super().__init__()
        self.localization = localization

    def localize(self) -> List[WeightedLocation]:
        self.localization.prepare()
        return self.localization.get_sorted_suggestions()


class GeneticRepair(LocalizationRepair, abc.ABC):
    def __init__(
        self,
        initial_candidate: Candidate,
        population_size: int,
        max_generations: int,
        w_mut: float,
    ):
        super().__init__()

    @abc.abstractmethod
    def select(self) -> List[Candidate]:
        pass

    @abc.abstractmethod
    def mutate(self, selection: Candidate) -> Collection[Candidate]:
        pass

    @abc.abstractmethod
    def crossover(
        self, parent_1: Candidate, parent_2: Candidate
    ) -> Collection[Candidate]:
        pass
