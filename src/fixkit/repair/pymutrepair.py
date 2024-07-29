"""
The pymutrepair module provides the necessary tools to repair a fault using MutRepair.
"""

import os
from typing import List, Optional

from fixkit.fitness.metric import GenProgFitness
from fixkit.genetic.crossover import OnePointCrossover
from fixkit.genetic.minimize import DDMutationMinimizer
from fixkit.genetic.operators import (
    ReplaceLogicalAndOperator,
    ReplaceLogicalOrOperator,
    ReplaceRelationalEqualOperator,
    ReplaceRelationalNotEqualOperator,
    ReplaceRelationalGreaterOperator,
    ReplaceRelationalGreaterEqualOperator,
    ReplaceRelationalSmallerOperator,
    ReplaceRelationalSmallerEqualOperator,
    ReplaceUnaryNotOperator,
    ReplaceUnaryInvertOperator
)
from fixkit.genetic.selection import UniversalSelection, Selection
from fixkit.localization import Localization
from fixkit.localization.location import WeightedLocation
from fixkit.repair.repair import GeneticRepair
from fixkit.search.search import ExhaustiveStrategy, SearchStrategy


class PyMutRepair(GeneticRepair):
    """
    Class for repairing a fault using MutRepair.
    """

    def __init__(
        self,
        src: os.PathLike,
        localization: Localization,
        max_generations: int,
        w_mut: float,
        selection: Selection = None,
        workers: int = 1,
        out: os.PathLike = None,
        w_pos_t: float = 1,
        w_neg_t: float = 10,
        is_t4p: bool = False,
        excludes: Optional[List[str]] = None,
        line_mode: bool = False,
    ):
        """
        Initialize the GenProg repair.
        :param os.PathLike src: The source directory of the project.
        :param Localization localization: The localization to use for the repair.
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
            population_size=1,
            max_generations=max_generations,
            w_mut=w_mut,
            operators=[
                ReplaceLogicalAndOperator,
                ReplaceLogicalOrOperator,
                ReplaceRelationalEqualOperator,
                ReplaceRelationalNotEqualOperator,
                ReplaceRelationalGreaterOperator,
                ReplaceRelationalGreaterEqualOperator,
                ReplaceRelationalSmallerOperator,
                ReplaceRelationalSmallerEqualOperator,
                ReplaceUnaryNotOperator,
                ReplaceUnaryInvertOperator
            ],
            selection=selection or UniversalSelection(),
            crossover_operator=OnePointCrossover(),
            minimizer=DDMutationMinimizer(),
            workers=workers,
            out=out,
            is_t4p=is_t4p,
            excludes=excludes,
            line_mode=line_mode,
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
        max_generations: int,
        w_mut: float,
        selection: Selection = None,
        workers: int = 1,
        out: os.PathLike = None,
        w_pos_t: float = 1,
        w_neg_t: float = 10,
        is_t4p: bool = False,
        line_mode: bool = False,
    ) -> "PyMutRepair":
        """
        Create a GenProg repair from the source.
        :param os.PathLike src: The source directory of the project.
        :param Optional[List[str]] excludes: The set of files to exclude from the statement search.
        :param Localization localization: The localization to use for the repair.
        :param int max_generations: The maximum number of generations.
        :param float w_mut: The mutation rate, i.e., the probability of a mutation.
        :param Selection selection: The selection operator to use for the repair.
        :param int workers: The number of workers to use for the evaluation of the fitness.
        :param os.PathLike out: The working directory for the repair.
        :param float w_pos_t: The weight for the positive test cases.
        :param float w_neg_t: The weight for the negative test cases.
        :return PyGenProg: The GenProg repair created from the source.
        """
        return PyMutRepair(
            src=src,
            localization=localization,
            max_generations=max_generations,
            w_mut=w_mut,
            selection=selection,
            workers=workers,
            out=out,
            w_pos_t=w_pos_t,
            w_neg_t=w_neg_t,
            is_t4p=is_t4p,
            excludes=excludes,
            line_mode=line_mode,
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

    def get_search_strategy(self) -> SearchStrategy:
        return ExhaustiveStrategy(operators=self.operator, suggestions=self.suggestions)


__all__ = ["PyMutRepair"]
