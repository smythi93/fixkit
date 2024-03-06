import abc
import os
import random
from pathlib import Path
from typing import Collection, List, Type, Optional

from pyrep.candidate import Candidate, GeneticCandidate
from pyrep.constants import DEFAULT_WORK_DIR
from pyrep.fitness.engine import Engine
from pyrep.fitness.metric import Fitness
from pyrep.genetic.crossover import Crossover, OnePointCrossover
from pyrep.genetic.operators import MutationOperator
from pyrep.localization import Localization, WeightedLocation, WeightedIdentifier
from pyrep.normalization import normalize
from pyrep.selection import Selection, RandomSelection
from pyrep.stmt import StatementFinder


class Repair(abc.ABC):
    def __init__(self, out: os.PathLike = None):
        self.out = Path(out or DEFAULT_WORK_DIR)

    @abc.abstractmethod
    def repair(self):
        pass


class LocalizationRepair(Repair, abc.ABC):
    def __init__(self, localization: Localization, out: os.PathLike = None):
        super().__init__(out)
        self.localization = localization

    def localize(self) -> List[WeightedLocation]:
        self.localization.prepare()
        return self.localization.get_sorted_suggestions()


class GeneticRepair(LocalizationRepair, abc.ABC):
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
        workers: int = 1,
        out: os.PathLike = None,
    ):
        super().__init__(localization, out)
        self.initial_candidate = initial_candidate
        self.population: List[GeneticCandidate] = [self.initial_candidate]
        self.choices = list(self.initial_candidate.statements.keys())
        self.fitness = Engine(fitness, workers, self.out)
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

    @staticmethod
    def get_initial_candidate(
        src: os.PathLike, excludes: Optional[str]
    ) -> GeneticCandidate:
        statement_finder = StatementFinder(src=Path(src), excludes=excludes)
        statement_finder.search_source()
        return GeneticCandidate.from_candidate(statement_finder.build_candidate())

    @staticmethod
    @abc.abstractmethod
    def from_source(src: os.PathLike, *args, **kwargs) -> "GeneticRepair":
        return NotImplemented

    def repair(self) -> List[GeneticCandidate]:
        suggestions = self.localize()
        normalize(suggestions)
        self.set_suggestions(suggestions)
        self.fill_population()
        # self.filter_population()
        self.fitness.evaluate(self.population)
        if not self.abort():
            for _ in range(self.max_generations):
                self.iteration()
                if self.abort():
                    break
        fitness = max(c.fitness for c in self.population)
        self.population = [c for c in self.population if c.fitness == fitness]
        self.minimize_population()
        return self.population

    def abort(self) -> bool:
        return max(c.fitness for c in self.population) >= 1 - 1e-8

    def iteration(self):
        self.viable()
        self.select()
        self.crossover_population()
        self.mutate_population()
        # self.filter_population()
        self.fitness.evaluate(self.population)

    def set_suggestions(self, suggestions: List[WeightedLocation]):
        self.suggestions = list()
        for suggestion in suggestions:
            for identifier in self.initial_candidate.lines[suggestion.file][
                suggestion.line
            ]:
                self.suggestions.append(
                    WeightedIdentifier(identifier, suggestion.weight)
                )

    def viable(self):
        self.population = [c for c in self.population if c.fitness > 0]

    def select(self):
        self.population = self.selection.select(
            self.population, self.population_size // 2
        )

    def fill_population(self):
        new_population = self.population[:]
        while len(new_population) < self.population_size:
            new_population.append(
                random.choice(self.population).clone(change_gen=False)
            )
        self.population = new_population

    def crossover_population(self):
        random.shuffle(self.population)
        for parent_1, parent_2 in zip(
            self.population[: len(self.population) // 2],
            self.population[len(self.population) // 2 :],
        ):
            self.population.extend(self.crossover(parent_1, parent_2))

    def crossover(
        self, parent_1: Candidate, parent_2: Candidate
    ) -> Collection[Candidate]:
        return self.crossover_operator.crossover(parent_1, parent_2)

    def mutate_population(self):
        for candidate in self.population[:]:
            self.population.append(self.mutate(candidate))

    def mutate(self, selection: GeneticCandidate) -> GeneticCandidate:
        candidate = selection.clone()
        for location in self.suggestions:
            if self.mutate_constrain(location.weight):
                candidate.mutations.append(
                    random.choices(self.operator, weights=self.operator_weights, k=1)[
                        0
                    ](location.identifier, self.choices)
                )
        return candidate

    def mutate_constrain(self, weight: float) -> bool:
        return random.random() < weight and random.random() < self.w_mut

    def filter_population(self):
        self.population = list(set(self.population))

    def minimize_population(self):
        self.population = [self.minimize(c) for c in self.population]

    def minimize(self, candidate: GeneticCandidate) -> GeneticCandidate:
        n = 2
        while len(candidate) > 1:
            start = 0
            subset_length = len(candidate) / n
            is_reduced = False

            while start < len(candidate):
                subset = (
                    candidate[: int(start)] + candidate[int(start + subset_length) :]
                )
                new_candidate = candidate.offspring(subset, change_gen=False)
                self.fitness.evaluate(new_candidate)
                if new_candidate.fitness >= candidate.fitness:
                    candidate = new_candidate
                    n = max(n - 1, 2)
                    is_reduced = True
                    break

                start += subset_length

            if not is_reduced:
                if n == len(candidate):
                    break
                n = min(n * 2, len(candidate))
        return candidate
