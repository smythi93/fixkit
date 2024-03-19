"""
The repair module provides the necessary tools to repair a fault.
"""

import abc
import os
import random
from pathlib import Path
from typing import Collection, List, Type, Optional, Any

from pyrep.candidate import Candidate, GeneticCandidate
from pyrep.constants import DEFAULT_WORK_DIR
from pyrep.fitness.engine import Tests4PyEngine, Engine
from pyrep.fitness.metric import Fitness
from pyrep.genetic.crossover import Crossover, OnePointCrossover
from pyrep.genetic.minimize import MutationMinimizer, DefaultMutationMinimizer
from pyrep.genetic.operators import MutationOperator
from pyrep.genetic.selection import Selection, RandomSelection
from pyrep.localization import Localization
from pyrep.localization.location import WeightedIdentifier, WeightedLocation
from pyrep.localization.normalization import normalize
from pyrep.logger import LOGGER
from pyrep.stmt import StatementFinder


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
        line_mode: bool = False,
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
        """
        super().__init__(localization, out)
        self.initial_candidate = initial_candidate
        self.population: List[GeneticCandidate] = [self.initial_candidate]
        self.choices = list(self.initial_candidate.statements.keys())
        self.fitness = (Tests4PyEngine if is_t4p else Engine)(
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

    def repair(self) -> List[GeneticCandidate]:
        """
        Repair the fault using genetic programming.
        :return List[GeneticCandidate]: The list of candidates that repair (or perform best) the fault.
        """
        # Localize the faults.
        LOGGER.info("Localizing the faulty code locations.")
        suggestions = self.localize()
        normalize(suggestions)
        self.set_suggestions(suggestions)

        # Evaluate the fitness for the initial candidate to reduce overhead.
        LOGGER.info("Evaluating the fitness for the initial candidate.")
        self.fitness.evaluate(self.population)

        if not self.abort():
            # Fill the population and evaluate the fitness.
            LOGGER.info(
                "Filling the population and evaluating the fitness of each candidate."
            )
            self.fill_population()
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

        # Minimize the population and return the best candidates.
        fitness = max(c.fitness for c in self.population)
        LOGGER.info("The best candidate has a fitness of %.2f.", fitness)
        self.population = [c for c in self.population if c.fitness == fitness]
        self.filter_population()
        LOGGER.info("Minimize the best candidates.")
        self.population = self.minimizer.minimize(self.population)
        LOGGER.info("Found %d possible repairs.", len(self.population))
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
        # Filter the population and select the best candidates.
        LOGGER.info("Filtering the population and selecting the best candidates.")
        self.viable()
        self.select()

        # Crossover and mutate the population.
        LOGGER.info("Crossover the population.")
        self.crossover_population()
        LOGGER.info("Mutate the population.")
        self.mutate_population()

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

    def viable(self):
        """
        Filter the population to keep only viable candidates whose fitness is greater than 0.
        """
        self.population = [c for c in self.population if c.fitness > 0]
        if not self.population:
            LOGGER.info("No viable candidates, start with new population.")
            self.population = [self.initial_candidate]
            self.fill_population()
    def select(self):
        """
        Select the best candidates from the population for the next generation.
        """
        self.population = self.selection.select(
            self.population, self.population_size // 2
        )

    def fill_population(self):
        """
        Fill the population with clones of the initial candidate.
        """
        new_population = self.population[:]
        while len(new_population) < self.population_size:
            new_population.append(
                random.choice(self.population).clone(change_gen=False)
            )
        self.population = new_population

    def crossover_population(self):
        """
        Crossover the population to create new candidates.
        """
        random.shuffle(self.population)
        for parent_1, parent_2 in zip(
            self.population[: len(self.population) // 2],
            self.population[len(self.population) // 2 :],
        ):
            self.population.extend(self.crossover(parent_1, parent_2))

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

    def mutate_population(self):
        """
        Mutate the population to create new candidates by giving each candidate a chance to mutate.
        """
        for candidate in self.population[:]:
            self.population.append(self.mutate(candidate))

    def mutate(self, selection: GeneticCandidate) -> GeneticCandidate:
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
        return candidate

    def should_mutate(self, weight: float) -> bool:
        """
        Check if a mutation should occur based on the weight.
        :param float weight: The weight of the location.
        :return bool: True if a mutation should occur, False otherwise.
        """
        return random.random() < weight and random.random() < self.w_mut

    def filter_population(self):
        """
        Filter the population to remove duplicates.
        """
        self.population = list(set(self.population))
