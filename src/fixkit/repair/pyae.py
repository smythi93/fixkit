import abc
import os
from typing import List, Optional, Generator

from src.fixkit.candidate import GeneticCandidate, Candidate
from src.fixkit.fitness.metric import GenProgFitness
from src.fixkit.genetic.operators import (
    Delete,
    InsertBoth,
    InsertBefore,
    InsertAfter,
    MutationOperator,
)
from src.fixkit.localization.localization import Localization
from src.fixkit.repair.repair import GeneticRepair


class AbstractAE(GeneticRepair, abc.ABC):
    def __init__(
        self,
        initial_candidate: Candidate,
        localization: Localization,
        population_size: int,
        max_generations: int,
        k: int = 1,
        workers: int = 1,
        out: os.PathLike = None,
        w_pos_t: float = 1,
        w_neg_t: float = 10,
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
    ):
        self.metric = GenProgFitness(set(), set(), w_pos_t=w_pos_t, w_neg_t=w_neg_t)
        self.k = k
        super().__init__(
            initial_candidate=initial_candidate,
            fitness=self.metric,
            localization=localization,
            population_size=population_size,
            max_generations=max_generations,
            operators=[Delete, InsertAfter, InsertBefore],
            selection=None,
            crossover_operator=None,
            minimizer=None,
            workers=workers,
            out=out,
            is_t4p=is_t4p,
            is_system_test=is_system_test,
            system_tests=system_tests,
            line_mode=line_mode,
            w_mut=1,
        )

    @abc.abstractmethod
    def equivalent(self, candidate_1: GeneticCandidate, candidate_2: GeneticCandidate):
        pass

    @abc.abstractmethod
    def repair_strategy(self, model) -> Generator[MutationOperator, None, None]:
        pass

    @abc.abstractmethod
    def test_strategy(self, candidate: List[GeneticCandidate], model):
        pass

    def candidate_repairs(self, model) -> Generator[List[MutationOperator], None, None]:
        for i in range(1, self.k + 1):
            generators = [self.repair_strategy(model) for _ in range(i)]
            current_state = [next(generator) for generator in generators]
            yield current_state[:]
            current = 0
            while current < len(generators):
                try:
                    current_state[current] = next(generators[current])
                    current = max(0, current - 1)
                    yield current_state[:]
                except StopIteration:
                    generators[current] = self.repair_strategy(model)
                    current += 1

    def repair_loop(self):
        model = set()
        equivalent_classes = set()
        for candidate in self.candidate_repairs():
            pass


class AE(AbstractAE):
    pass
