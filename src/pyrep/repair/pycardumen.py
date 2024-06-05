"""
The pycardumen module provides the necessary tools to repair a fault using Cardumen.
"""

import ast
import os
import random
from typing import List, Optional, Collection

from pyrep.candidate import GeneticCandidate
from pyrep.fitness.metric import GenProgFitness
from pyrep.genetic.crossover import OnePointCrossover
from pyrep.genetic.minimize import DDMutationMinimizer
from pyrep.genetic.operators import Replace
from pyrep.genetic.selection import UniversalSelection, Selection
from pyrep.genetic.templates import Template, ProbabilisticModel, VarNamesCollector
from pyrep.localization import Localization
from pyrep.localization.location import WeightedLocation
from pyrep.repair.repair import GeneticRepair


class PyCardumen(GeneticRepair):
    """
    Class for repairing a fault using Cardumen.
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
        excludes: Optional[List[str]] = None,
        line_mode: bool = False,
    ):
        """
        Initialize the Cardumen repair.
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
            operators=[Replace],
            selection=selection or UniversalSelection(),
            crossover_operator=OnePointCrossover(),
            minimizer=DDMutationMinimizer(),
            workers=workers,
            out=out,
            is_t4p=is_t4p,
            excludes=excludes,
            line_mode=line_mode,
        )

        self.template_pool: List[Template] = list()
        for statement in self.initial_candidate.statements.values():
            self.template_pool.append(Template(statement))

        self.model = ProbabilisticModel(self.initial_candidate.statements)

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
        line_mode: bool = False,
    ) -> "PyCardumen":
        """
        Create a Cardumen repair from the source.
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
        return PyCardumen(
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

    def mutate(self, selection: GeneticCandidate) -> Collection[GeneticCandidate]:
        """
        Mutate a candidate to create a new candidate.
        :param GeneticCandidate selection: The candidate to mutate.
        :return GeneticCandidate: The new mutated candidate.
        """
        candidate = selection.clone()
        for location in self.suggestions:
            if self.should_mutate(location.weight):
                candidate.mutations.append(
                    Replace(location.identifier, self.choices)
                )
        return [candidate]  
    
    #TODO: die haben location filter local, package, global was guter python äquivalent? local (same file), folder, global
    #Würde gerne auf File Ebene bleiben und nicht die AST durchsuchen (falls wir auf Class Ebene gehen)
    def filter_template_pool(self, location: str, file: str, return_type: str = "return_type") -> List[Template]:
        pool: List[Template] = self.template_pool
        pool = [tmpl for tmpl in pool if tmpl.return_type == return_type]
        if location == "local":
            pool = [tmpl for tmpl in pool if tmpl.file == file]

        return pool

    def selecting_template(self, statement: ast.AST) -> Template:
        print(ast.unparse(statement))
        collector = VarNamesCollector()
        collector.visit(statement)
        var_statement = collector.vars
        weights = []
        # doesnt have the template of the statment a 1.0 probability??
        for template in self.template_pool:
            var_template = template.original_vars
            print(var_statement)
            print(var_template)
            print(sum(var in var_statement for var in var_template))
            print(len(var_template))
            weights.append(
                sum(var in var_statement for var in var_template) / len(var_template)
            )

        for tmpl, weight in zip(self.template_pool, weights):
            print(ast.unparse(tmpl.statement), weight)

        return random.choices(self.template_pool, weights, k=1)[0]


__all__ = ["PyCardumen"]
