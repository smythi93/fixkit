import abc
import random
from typing import List

import numpy.random

from pyrep.candidate import GeneticCandidate


class Selection:
    @abc.abstractmethod
    def select(
        self, population: List[GeneticCandidate], population_size: int
    ) -> List[GeneticCandidate]:
        pass


class RandomSelection(Selection):
    def select(
        self, population: List[GeneticCandidate], population_size: int
    ) -> List[GeneticCandidate]:
        if len(population) <= population_size:
            return population
        return random.sample(population, k=population_size)


class UniversalSelection(Selection):
    def select(
        self, population: List[GeneticCandidate], population_size: int
    ) -> List[GeneticCandidate]:
        if len(population) <= population_size:
            return population
        return numpy.random.choice(
            population,
            size=population_size,
            replace=False,
            p=[c.fitness for c in population],
        ).tolist()


class TournamentSelection(Selection):
    def __init__(self, tournament_size: int):
        self.tournament_size = tournament_size

    def select(
        self, population: List[GeneticCandidate], population_size: int
    ) -> List[GeneticCandidate]:
        if len(population) <= population_size:
            return population
        population = population[:]
        candidates = list()
        for _ in range(population_size):
            tournament = random.sample(population, k=self.tournament_size)
            choice = numpy.random.choice(
                tournament, size=1, p=[c.fitness for c in tournament]
            )[0]
            candidates.append(choice)
            population.remove(choice)
        return candidates
