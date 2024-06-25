"""
The repair module provides the necessary tools to repair a fault.
"""

import abc
import os
import random
from pathlib import Path
from typing import Collection, List, Type, Optional, Any

from fixkit.candidate import Candidate, GeneticCandidate
from fixkit.constants import DEFAULT_WORK_DIR
from fixkit.fitness.engine import (
    Tests4PyEngine,
    ParallelEngine,
    Tests4PySystemTestEngine,
    Tests4PySequentialEngine,
    Tests4PySystemTestSequentialEngine,
    SequentialEngine,
)
from fixkit.fitness.metric import Fitness
from fixkit.genetic.crossover import Crossover, OnePointCrossover
from fixkit.genetic.minimize import MutationMinimizer, DefaultMutationMinimizer
from fixkit.genetic.operators import MutationOperator
from fixkit.genetic.selection import Selection, RandomSelection
from fixkit.genetic.types import Population
from fixkit.localization import Localization
from fixkit.localization.location import WeightedIdentifier, WeightedLocation
from fixkit.localization.normalization import normalize
from fixkit.logger import LOGGER
from fixkit.search.search import EvolutionaryStrategy, SearchStrategy
from fixkit.stmt import StatementFinder


class Repair(abc.ABC):
    """
    Abstract class for repairing a fault.
    """

    def __init__(self, out: os.PathLike = None):
        """
        Initialize the repair.
        :param os.PathLike out: The working directory for the repair.
        """
        self.out = Path(out or DEFAULT_WORK_DIR)

    @abc.abstractmethod
    def repair(self) -> Any:
        """
        Abstract method for repairing a fault.
        :return Any: The result of the repair.
        """
        pass


class LocalizationRepair(Repair, abc.ABC):
    """
    Abstract class for repairing a fault using localization.
    """

    def __init__(self, localization: Localization, out: os.PathLike = None):
        """
        Initialize the localization repair.
        :param Localization localization: The localization to use for the repair.
        :param os.PathLike out: The working directory for the repair.
        """
        super().__init__(out)
        self.localization = localization

    def localize(self) -> List[WeightedLocation]:
        """
        Localize the fault using the localization.
        :return List[WeightedLocation]: The list of weighted locations.
        """
        self.localization.prepare()
        return self.localization.get_sorted_suggestions()


class GeneticRepair(LocalizationRepair, abc.ABC):
    """
    Abstract class for repairing a fault using genetic programming.
    """

    def __init__(
        self,
        initial_candidate: GeneticCandidate,
        fitness: Fitness,
        localization: Localization,
        population_size: int,
        max_generations: int,
        w_mut: float,
        operators: Collection[Type[MutationOperator]],
        operator_weights: Optional[List[float]] = None,
        selection: Selection = None,
        crossover_operator: Crossover = None,
        minimizer: Optional[MutationMinimizer] = None,
        workers: int = 1,
        out: os.PathLike = None,
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
        serial: bool = False,
    ):
        """
        Initialize the genetic repair.
        :param GeneticCandidate initial_candidate: The initial candidate to start the repair.
        :param Fitness fitness: The fitness to use for the repair.
        :param Localization localization: The localization to use for the repair.
        :param int population_size: The size of the population.
        :param int max_generations: The maximum number of generations.
        :param float w_mut: The mutation rate, i.e., the probability of a mutation.
        :param Collection[Type[MutationOperator]] operators: The mutation operator classes to use for the repair.
        :param Optional[List[float]] operator_weights: The weights of the mutation operators, i.e., the probability of
        each operator. Default will be a uniform distribution.
        :param Selection selection: The selection operator to use for the repair.
        :param Crossover crossover_operator: The crossover operator to use for the repair.
        :param int workers: The number of workers to use for the evaluation of the fitness.
        :param os.PathLike out: The working directory for the repair.
        :param bool is_t4p: True if the repair is using Tests4Py, False otherwise.
        :param bool is_system_test: True if the repair is using system tests, False otherwise.
        :param os.PathLike | List[os.PathLike] system_tests: The system tests to use for the repair. This argument is
        only considered when is_system_test is True.
        :param bool line_mode: True if the line mode is enabled, False otherwise.
        """
        super().__init__(localization, out)
        self.initial_candidate: GeneticCandidate = initial_candidate
        self.population: Population = [self.initial_candidate]
        self.choices: List[int] = list(self.initial_candidate.statements.keys())
        if serial:
            if is_t4p:
                if is_system_test:
                    if system_tests is None:
                        raise ValueError("System tests must be provided.")
                    self.fitness = Tests4PySystemTestSequentialEngine(
                        fitness=fitness, tests=system_tests, out=self.out
                    )
                else:
                    self.fitness = Tests4PySequentialEngine(
                        fitness=fitness, out=self.out
                    )
            else:
                self.fitness = SequentialEngine(fitness=fitness, out=self.out)
        elif is_t4p:
            if is_system_test:
                if system_tests is None:
                    raise ValueError("System tests must be provided.")
                self.fitness = Tests4PySystemTestEngine(
                    fitness=fitness, tests=system_tests, workers=workers, out=self.out
                )
            else:
                self.fitness = Tests4PyEngine(
                    fitness=fitness, workers=workers, out=self.out
                )
        else:
            self.fitness = ParallelEngine(
                fitness=fitness, workers=workers, out=self.out
            )
        self.population_size = population_size
        self.max_generations = max_generations
        self.w_mut = w_mut
        self.suggestions: List[WeightedIdentifier] = []
        self.operator = operators
        self.operator_weights = operator_weights or [1 / len(operators)] * len(
            operators
        )
        self.selection = selection or RandomSelection()
        self.crossover_operator = crossover_operator or OnePointCrossover()
        self.minimizer = minimizer or DefaultMutationMinimizer()
        self.minimizer.fitness = self.fitness
        self.line_mode = line_mode
        self.strategy = None

    def get_search_strategy(self) -> SearchStrategy:
        return EvolutionaryStrategy(
            viable=self.viable,
            select=self.select,
            crossover=self.crossover_population,
            mutate=self.mutate_population,
        )

    @staticmethod
    def get_initial_candidate(
        src: os.PathLike, excludes: Optional[str], line_mode: bool = False
    ) -> GeneticCandidate:
        """
        Get the initial candidate from the source.
        :param os.PathLike src: The source directory of the project.
        :param Optional[List[str]] excludes: The list of files to exclude from the search.
        :param bool line_mode: True if the line mode is enabled, False otherwise.
        :return GeneticCandidate: The initial candidate.
        """
        LOGGER.info("Searching for statements in the source.")
        statement_finder = StatementFinder(
            src=Path(src), excludes=excludes, line_mode=line_mode
        )
        statement_finder.search_source()
        LOGGER.info("Building the initial candidate.")
        return GeneticCandidate.from_candidate(statement_finder.build_candidate())

    @staticmethod
    @abc.abstractmethod
    def from_source(src: os.PathLike, *args, **kwargs) -> "GeneticRepair":
        """
        Abstract method for creating a genetic repair from the source.
        :param os.PathLike src: The source directory of the project.
        :param args: A list of arguments.
        :param kwargs: A dictionary of keyword arguments.
        :return GeneticRepair: The genetic repair created from the source.
        """
        return NotImplemented

    def prepare_repair(self) -> Population:
        # Localize the faults.
        LOGGER.info("Localizing the faulty code locations.")
        suggestions = self.localize()
        normalize(suggestions)
        self.set_suggestions(suggestions)

        # Evaluate the fitness for the initial candidate to reduce overhead.
        LOGGER.info("Evaluating the fitness for the initial candidate.")
        self.fitness.evaluate(self.population)
        self.strategy = self.get_search_strategy()

    def repair_loop(self):
        if not self.abort():
            # Fill the population and evaluate the fitness.
            LOGGER.info(
                "Filling the population and evaluating the fitness of each candidate."
            )
            self.population = self.fill_population(self.population)
            self.fitness.evaluate(self.population)

            # Iterate until the maximum number of generations is reached or the fault is repaired.
            for gen in range(self.max_generations):
                LOGGER.info(f"Generation {gen + 1}/{self.max_generations}:")
                self.iteration()
                if self.abort():
                    LOGGER.info("Found a repair for the fault.")
                    break
            else:
                LOGGER.info(
                    "Reached the maximum number of generations without finding an appropriate repair."
                )
        else:
            LOGGER.info("The fault is already repaired.")

    def finalize_repair(self):
        # Minimize the population and return the best candidates.
        fitness = max(c.fitness for c in self.population)
        LOGGER.info("The best candidate has a fitness of %.2f.", fitness)
        self.population = [c for c in self.population if c.fitness == fitness]
        self.population = self.filter_population(self.population)
        LOGGER.info("Minimize the best candidates.")
        self.population = self.minimizer.minimize(self.population)
        LOGGER.info("Found %d possible repairs.", len(self.population))

    def repair(self) -> Population:
        """
        Repair the fault using genetic programming.
        :return Population: The list of candidates that repair (or perform best) the fault.
        """
        self.prepare_repair()

        self.repair_loop()

        self.finalize_repair()

        return self.population

    def abort(self) -> bool:
        """
        Check if the repair should be aborted.
        :return bool: True if the repair should be aborted, False otherwise.
        """
        return max(c.fitness for c in self.population) >= 1 - 1e-8

    def iteration(self):
        """
        Perform an iteration of the genetic programming.
        """
        self.population = self.prepare_population(self.population)
        self.population = self.strategy.search(self.population)
        # Evaluate the fitness for the population.
        LOGGER.info("Evaluate the fitness for the population.")
        self.fitness.evaluate(self.population)

    def set_suggestions(self, suggestions: List[WeightedLocation]):
        """
        Set the suggestions for the repair by mapping WeightedLocation to WeightedIdentifier.
        :param List[WeightedLocation] suggestions: The list of weighted locations.
        """
        self.suggestions = list()
        for suggestion in suggestions:
            if (
                suggestion.file in self.initial_candidate.lines
                and suggestion.line in self.initial_candidate.lines[suggestion.file]
            ):
                for identifier in self.initial_candidate.lines[suggestion.file][
                    suggestion.line
                ]:
                    self.suggestions.append(
                        WeightedIdentifier(identifier, suggestion.weight)
                    )

    # noinspection PyMethodMayBeStatic
    def prepare_population(self, population: Population) -> Population:
        """
        Prepare the population for the next generation.
        """
        return population

    def viable(self, population: Population) -> Population:
        """
        Filter the population to keep only viable candidates whose fitness is greater than 0.
        """
        population = [c for c in population if c.fitness > 0]
        if not population:
            LOGGER.info("No viable candidates, start with new population.")
            population = [self.initial_candidate]
            population = self.fill_population(population)
        return population

    def select(self, population: Population) -> Population:
        """
        Select the best candidates from the population for the next generation.
        """
        return self.selection.select(population, self.population_size // 2)

    def fill_population(self, population: Population) -> Population:
        """
        Fill the population with clones of the initial candidate.
        """
        new_population = population[:]
        while len(new_population) < self.population_size:
            new_population.append(random.choice(population).clone(change_gen=False))
        return new_population

    def crossover_population(self, population: Population) -> Population:
        """
        Crossover the population to create new candidates.
        """
        population = population[:]
        random.shuffle(population)
        for parent_1, parent_2 in zip(
            population[: len(population) // 2],
            population[len(population) // 2 :],
        ):
            population.extend(self.crossover(parent_1, parent_2))
        return population

    def crossover(
        self, parent_1: GeneticCandidate, parent_2: GeneticCandidate
    ) -> Collection[GeneticCandidate]:
        """
        Crossover two candidates to create new candidates.
        :param Candidate parent_1: The first parent candidate.
        :param Candidate parent_2: The second parent candidate.
        :return Collection[Candidate]: The collection of the new candidate offsprings.
        """
        return self.crossover_operator.crossover(parent_1, parent_2)

    def mutate_population(self, population: Population) -> Population:
        """
        Mutate the population to create new candidates by giving each candidate a chance to mutate.
        """
        population = population[:]
        for candidate in population[:]:
            population.extend(self.mutate(candidate))
        return population

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
                    random.choices(self.operator, weights=self.operator_weights, k=1)[
                        0
                    ](location.identifier, self.choices)
                )
        return [candidate]

    def should_mutate(self, weight: float) -> bool:
        """
        Check if a mutation should occur based on the weight.
        :param float weight: The weight of the location.
        :return bool: True if a mutation should occur, False otherwise.
        """
        return random.random() < weight and random.random() < self.w_mut

    # noinspection PyMethodMayBeStatic
    def filter_population(self, population: Population) -> Population:
        """
        Filter the population to remove duplicates.
        """
        return list(set(population))
