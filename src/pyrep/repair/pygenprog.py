import os
import random
from typing import List, Optional

from pyrep.candidate import Candidate, GeneticCandidate
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
            initial_candidate=initial_candidate,
            fitness=self.metric,
            localization=localization,
            population_size=population_size,
            max_generations=max_generations,
            w_mut=w_mut,
            operators=[Delete, InsertBoth, Replace],
            selection=selection or UniversalSelection(),
            crossover_operator=OnePointCrossover(),
            workers=workers,
            out=out,
        )

    @staticmethod
    def from_source(
        src: os.PathLike, excludes: Optional[List[str]] = None, *args, **kwargs
    ) -> "GeneticRepair":
        return PyGenProg._from_source(src, excludes, *args, **kwargs)

    @staticmethod
    def _from_source(
        src: os.PathLike,
        excludes: Optional[List[str]],
        localization: Localization,
        population_size: int,
        max_generations: int,
        w_mut: float,
        selection: Selection = None,
        workers: int = 1,
        out: os.PathLike = None,
        w_pos_t: float = 1,
        w_neg_t: float = 10,
    ) -> "PyGenProg":
        return PyGenProg(
            initial_candidate=PyGenProg.get_initial_candidate(src, excludes),
            localization=localization,
            population_size=population_size,
            max_generations=max_generations,
            w_mut=w_mut,
            selection=selection,
            workers=workers,
            out=out,
            w_pos_t=w_pos_t,
            w_neg_t=w_neg_t,
        )

    def localize(self) -> List[WeightedLocation]:
        suggestions = super().localize()
        self.metric.passing, self.metric.failing = (
            self.localization.passing,
            self.localization.failing,
        )
        return suggestions


class SingleMutationPyGenProg(PyGenProg):
    def mutate(self, selection: GeneticCandidate) -> GeneticCandidate:
        candidate = selection.clone()
        location = random.choices(
            self.suggestions, weights=[s.weight for s in self.suggestions], k=1
        )[0]
        candidate.mutations.append(
            random.choices(self.operator, weights=self.operator_weights, k=1)[0](
                location.identifier, self.choices
            )
        )
        return candidate
