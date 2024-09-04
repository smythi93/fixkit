"""
The pygenprog module provides the necessary tools to repair a fault using GenProg.
"""

import os
import random
from typing import List, Optional, Collection

from fixkit.candidate import Candidate, GeneticCandidate
from fixkit.fitness.metric import GenProgFitness
from fixkit.genetic.crossover import OnePointCrossover
from fixkit.genetic.minimize import DDMutationMinimizer
from fixkit.genetic.operators import Delete, InsertBoth, Replace
from fixkit.localization import Localization
from fixkit.localization.location import WeightedLocation
from fixkit.repair.repair import GeneticRepair
from fixkit.genetic.selection import UniversalSelection, Selection
from fixkit.genetic.minimize import MutationMinimizer
class PyGenProg(GeneticRepair):
    """
    Class for repairing a fault using GenProg.
    """

    def __init__(
        self,
        src: os.PathLike,
        localization: Localization,
        population_size: int,
        max_generations: int,
        w_mut: float,
        selection: Selection = None,
        workers: int = 1,
        out: os.PathLike = None,
        w_pos_t: float = 1,
        w_neg_t: float = 10,
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
        excludes: Optional[List[str]] = None,
        minimizer: Optional[MutationMinimizer] = None,
    ):
        """
        Initialize the GenProg repair.
        :param GeneticCandidate initial_candidate: The initial candidate to start the repair.
        :param Localization localization: The localization to use for the repair.
        :param int population_size: The size of the population.
        :param int max_generations: The maximum number of generations.
        :param float w_mut: The mutation rate, i.e., the probability of a mutation.
        :param Selection selection: The selection operator to use for the repair.
        :param int workers: The number of workers to use for the evaluation of the fitness.
        :param os.PathLike out: The working directory for the repair.
        :param float w_pos_t: The weight for the positive test cases.
        :param float w_neg_t: The weight for the negative test cases.
        """
        self.metric = GenProgFitness(set(), set(), w_pos_t=w_pos_t, w_neg_t=w_neg_t)
        super().__init__(
            src=src,
            fitness=self.metric,
            localization=localization,
            population_size=population_size,
            max_generations=max_generations,
            w_mut=w_mut,
            operators=[Delete, InsertBoth, Replace],
            selection=selection or UniversalSelection(),
            crossover_operator=OnePointCrossover(),
            minimizer=minimizer or DDMutationMinimizer(),
            workers=workers,
            out=out,
            is_t4p=is_t4p,
            is_system_test=is_system_test,
            system_tests=system_tests,
            line_mode=line_mode,
            excludes=excludes,
        )

    @classmethod
    def from_source(
        cls, src: os.PathLike, excludes: Optional[List[str]] = None, *args, **kwargs
    ) -> "GeneticRepair":
        """
        Abstract method for creating a genetic repair from the source.
        :param os.PathLike src: The source directory of the project.
        :param Optional[List[str]] excludes: The set of files to exclude from the statement search.
        :param args: A list of arguments.
        :param kwargs: A dictionary of keyword arguments.
        :return GeneticRepair: The genetic repair created from the source.
        """
        return cls._from_source(src, excludes, *args, **kwargs)

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
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
        minimizer: Optional[MutationMinimizer] = None,
    ) -> "PyGenProg":
        """
        Create a GenProg repair from the source.
        :param os.PathLike src: The source directory of the project.
        :param Optional[List[str]] excludes: The set of files to exclude from the statement search.
        :param Localization localization: The localization to use for the repair.
        :param int population_size: The size of the population.
        :param int max_generations: The maximum number of generations.
        :param float w_mut: The mutation rate, i.e., the probability of a mutation.
        :param Selection selection: The selection operator to use for the repair.
        :param int workers: The number of workers to use for the evaluation of the fitness.
        :param os.PathLike out: The working directory for the repair.
        :param float w_pos_t: The weight for the positive test cases.
        :param float w_neg_t: The weight for the negative test cases.
        :return PyGenProg: The GenProg repair created from the source.
        """
        return PyGenProg(
            src=src,
            localization=localization,
            population_size=population_size,
            max_generations=max_generations,
            w_mut=w_mut,
            selection=selection,
            workers=workers,
            out=out,
            w_pos_t=w_pos_t,
            w_neg_t=w_neg_t,
            is_t4p=is_t4p,
            is_system_test=is_system_test,
            system_tests=system_tests,
            line_mode=line_mode,
            excludes=excludes,
            minimizer=minimizer,
        )

    def localize(self) -> List[WeightedLocation]:
        """
        Localize the fault using the localization and report the passing and failing tests to the metric.
        :return List[WeightedLocation]: The list of weighted locations.
        """
        suggestions = super().localize()
        self.metric.passing, self.metric.failing = (
            self.localization.passing,
            self.localization.failing,
        )
        return suggestions


class SingleMutationPyGenProg(PyGenProg):
    """
    Class for repairing a fault using GenProg with a single mutation.
    """

    def mutate(self, selection: GeneticCandidate) -> Collection[GeneticCandidate]:
        """
        Mutate the given selection by adding a single mutation.
        :param GeneticCandidate selection: The candidate to mutate.
        :return GeneticCandidate: The mutated candidate.
        """
        candidate = selection.clone()
        location = random.choices(
            self.suggestions, weights=[s.weight for s in self.suggestions], k=1
        )[0]
        candidate.mutations.append(
            random.choices(self.operator, weights=self.operator_weights, k=1)[0](
                location.identifier, self.choices
            )
        )
        return [candidate]

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
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
        minimizer: Optional[MutationMinimizer]= None,
    ) -> "SingleMutationPyGenProg":
        """
        Create a GenProg repair from the source.
        :param os.PathLike src: The source directory of the project.
        :param Optional[List[str]] excludes: The set of files to exclude from the statement search.
        :param Localization localization: The localization to use for the repair.
        :param int population_size: The size of the population.
        :param int max_generations: The maximum number of generations.
        :param float w_mut: The mutation rate, i.e., the probability of a mutation.
        :param Selection selection: The selection operator to use for the repair.
        :param int workers: The number of workers to use for the evaluation of the fitness.
        :param os.PathLike out: The working directory for the repair.
        :param float w_pos_t: The weight for the positive test cases.
        :param float w_neg_t: The weight for the negative test cases.
        :return SingleMutationPyGenProg: The GenProg repair created from the source.
        """
        return SingleMutationPyGenProg(
            src=src,
            localization=localization,
            population_size=population_size,
            max_generations=max_generations,
            w_mut=w_mut,
            selection=selection,
            workers=workers,
            out=out,
            w_pos_t=w_pos_t,
            w_neg_t=w_neg_t,
            is_t4p=is_t4p,
            is_system_test=is_system_test,
            system_tests=system_tests,
            line_mode=line_mode,
            excludes=excludes,
            minimizer=minimizer,
        )


__all__ = ["PyGenProg", "SingleMutationPyGenProg"]
