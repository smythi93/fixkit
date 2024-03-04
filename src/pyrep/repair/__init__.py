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
        initial_candidate: Candidate,
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
        self.initial_candidate = GeneticCandidate.from_candidate(initial_candidate)
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

    def repair(self) -> List[GeneticCandidate]:
        self.set_suggestions(normalize(self.localize()))
        for _ in range(self.max_generations):
            self.iteration()
            if max(c.fitness for c in self.population) == 1:
                break
        fitness = max(c.fitness for c in self.population)
        return [c for c in self.population if c.fitness == fitness]

    def iteration(self):
        self.population = self.select()
        self.crossover_population()
        self.mutate_population()
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

    def mutate_population(self):
        for candidate in self.population[:]:
            self.population.append(self.mutate(candidate))

    def select(self) -> List[Candidate]:
        return self.selection.select(self.population, self.population_size // 2)

    def mutate(self, selection: GeneticCandidate) -> GeneticCandidate:
        candidate = selection.clone()
        for location in self.suggestions:
            if random.random() < location.weight and random.random() < self.w_mut:
                candidate.mutations.append(
                    random.choices(self.operator, weights=self.operator_weights, k=1)[
                        0
                    ](location.identifier, self.choices)
                )
        return candidate

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
        return [
            parent_1,
            parent_2,
            *self.crossover_operator.crossover(parent_1, parent_2),
        ]
