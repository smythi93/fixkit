import os
from typing import List

from pyrep.candidate import Candidate
from pyrep.fitness.metric import GenProgFitness
from pyrep.genetic.crossover import OnePointCrossover
from pyrep.genetic.operators import Delete, InsertBoth, Replace
from pyrep.localization import Localization, WeightedLocation
from pyrep.repair import GeneticRepair
from pyrep.selection import UniversalSelection, Selection


class PyGenProg(GeneticRepair):
    def __init__(
        self,
        initial_candidate: Candidate,
        localization: Localization,
        population_size: int,
        max_generations: int,
        w_mut: float,
        selection: Selection = None,
        workers: int = 1,
        out: os.PathLike = None,
        w_pos_t: float = 1,
        w_neg_t: float = 10,
    ):
        self.metric = GenProgFitness(set(), set(), w_pos_t=w_pos_t, w_neg_t=w_neg_t)
        super().__init__(
            initial_candidate,
            self.metric,
            localization,
            population_size,
            max_generations,
            w_mut,
            [Delete, InsertBoth, Replace],
            selection or UniversalSelection(),
            OnePointCrossover(),
            workers,
            out,
        )

    def localize(self) -> List[WeightedLocation]:
        suggestions = super().localize()
        self.metric.passing, self.metric.failing = (
            self.localization.passing,
            self.localization.failing,
        )
        return suggestions
