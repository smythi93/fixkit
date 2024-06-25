"""
The pycardumen module provides the necessary tools to repair a fault using Cardumen.
"""

import ast
import os
import random
from copy import deepcopy
from typing import List, Optional, Collection

from fixkit.candidate import GeneticCandidate
from fixkit.fitness.metric import GenProgFitness
from fixkit.genetic.crossover import OnePointCrossover
from fixkit.genetic.minimize import DDMutationMinimizer
from fixkit.genetic.operators import ReplaceCardumen
from fixkit.genetic.selection import UniversalSelection, Selection
from fixkit.genetic.templates import (
    Template,
    TemplateInstance,
    TemplateInstanceGenerator,
    ProbabilisticModel,
    VarNamesCollector,
    Scope_Constructor,
    Scope,
)
from fixkit.localization import Localization
from fixkit.localization.location import WeightedLocation
from fixkit.logger import info_logger
from fixkit.repair.repair import GeneticRepair


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
        :param os.PathLike src: The source directory of the project.
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
            operators=[ReplaceCardumen],
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
        statements = self.initial_candidate.statements
        files = self.statement_finder.files
        for id in statements:
            self.template_pool.append(Template(statements[id], files[id]))

        collector = Scope_Constructor()
        # the trees of all the files of the program to be repaired
        trees = self.statement_finder.trees
        for tree in trees.values():
            collector.search(tree)
        self.scope_stmt = collector.scope_stmt

        # model
        self.model = ProbabilisticModel(self.initial_candidate.statements)
        info_logger()

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
                collector = Scope_Constructor()
                for tree in candidate.trees.values():
                    collector.search(tree)
                scope_stmt = collector.scope_stmt
                statement = candidate.statements[location.identifier]
                file = self.statement_finder.files[location.identifier]
                tmpl_pool = self.filter_template_pool("local", file, statement)
                tmpl = self.selecting_template(tmpl_pool, statement)
                tmpl_instances = self.instance_template(tmpl, statement, scope_stmt)
                tmpl_instance = self.selecting_template_instance(
                    candidate.statements, tmpl_instances
                )

                candidate.mutations.append(
                    ReplaceCardumen(location.identifier, tmpl_instance)
                )
        return [candidate]

    def filter_template_pool(
        self, location: str, file: str, statement: ast.AST, code_type_mode: bool = False
    ) -> List[Template]:
        """
        Filters the template pool by Location and Target_Code_Type (by default False)
        Location -> local, folder, global
        code_type_mode -> True, False
        """
        pool: List[Template] = self.template_pool
        if code_type_mode:
            pool = [
                tmpl
                for tmpl in pool
                if tmpl.target_code_type == type(statement).__name__
            ]
        if location == "local":
            pool = [tmpl for tmpl in pool if tmpl.path == file]
        elif location == "folder":
            pool = [
                tmpl
                for tmpl in pool
                if os.path.dirname(tmpl.path) == os.path.dirname(file)
            ]

        return pool

    def selecting_template(
        self, template_pool: List[Template], statement: ast.AST
    ) -> Template:
        """
        Selects a Template from the Pool by weighted random choice.
        The weights are (How many Template Var are in the Statement / All Var in Template)
        f.e.
        Template 5 Vars and 3 of these Var are in the Statement -> 3/5
        """
        collector = VarNamesCollector()
        collector.visit(statement)
        var_in_statement = collector.vars
        weights = []

        for template in template_pool:
            collector = VarNamesCollector()
            collector.visit(template.statement)
            var_in_template = collector.vars
            var_in_statement_copy = deepcopy(var_in_statement)
            count = 0
            for var in var_in_template:
                if var in var_in_statement_copy:
                    count += 1
                    var_in_statement_copy.remove(var)
            weights.append(count / len(var_in_template))

        return random.choices(population=template_pool, weights=weights, k=1)[0]

    def instance_template(
        self,
        template: Template,
        statement: ast.AST,
        scope_stmt: dict[ast.AST, list[Scope]],
    ) -> List[TemplateInstance]:
        """
        Creates TemplateInstances from a Template. Collects all Vars in Scope
        and creates all possible combinations of the Template.
        """
        vars_in_scope = set()

        for scope in scope_stmt[statement]:
            for var in scope.vars:
                vars_in_scope.add(var)

        generator = TemplateInstanceGenerator(template)
        tmpl_instances = generator.construct_all_Combinations(vars_in_scope)

        return tmpl_instances

    def selecting_template_instance(
        self, statements: dict[int, ast.AST], tmpl_instances: List[TemplateInstance]
    ) -> ast.AST:
        """
        Selects a Template Instance by random weighted choice.
        """
        probabilities = {}
        for instance in tmpl_instances:
            probabilities[instance] = self.model.probabilities[
                instance.combination.items
            ]

        lucky_one = random.choices(
            list(probabilities.keys()), list(probabilities.values()), k=1
        )[0]

        return lucky_one


__all__ = ["PyCardumen"]
