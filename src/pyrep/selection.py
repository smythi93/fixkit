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
        fitness = numpy.array([c.fitness for c in population], dtype=float)
        array = numpy.empty(len(population), dtype=GeneticCandidate)
        array[:] = population[:]
        return numpy.random.choice(
            array,
            size=population_size,
            replace=False,
            p=fitness / sum(fitness),
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
            fitness = numpy.array([c.fitness for c in tournament], dtype=float)
            array = numpy.empty(len(tournament), dtype=GeneticCandidate)
            array[:] = tournament[:]
            choice = numpy.random.choice(
                array,
                size=1,
                p=fitness / sum(fitness),
            )[0]
            candidates.append(choice)
            population.remove(choice)
        return candidates
