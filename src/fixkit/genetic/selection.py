"""
The selection module provides the necessary tools to select candidates from a population.
"""

import abc
import random
from typing import List

import numpy.random

from fixkit.candidate import GeneticCandidate
from fixkit.constants import EPSILON


class Selection(abc.ABC):
    """
    Abstract class for selection operators.
    """

    @abc.abstractmethod
    def select(
        self, population: List[GeneticCandidate], population_size: int
    ) -> List[GeneticCandidate]:
        """
        Abstract method for selecting candidates from a population.
        :param List[GeneticCandidate] population: The population to select from.
        :param int population_size: The size of the population to select.
        :return List[GeneticCandidate]: The selected population.
        """
        pass


class RandomSelection(Selection):
    """
    Random selection operator.
    """

    def select(
        self, population: List[GeneticCandidate], population_size: int
    ) -> List[GeneticCandidate]:
        """
        Select a random population from the given population.
        :param List[GeneticCandidate] population: The population to select from.
        :param int population_size: The size of the population to select.
        :return List[GeneticCandidate]: The selected population.
        """
        if len(population) <= population_size:
            return population
        return random.sample(population, k=population_size)


class UniversalSelection(Selection):
    def select(
        self, population: List[GeneticCandidate], population_size: int
    ) -> List[GeneticCandidate]:
        """
        Select a population from the given population using the universal selection method.
        :param List[GeneticCandidate] population: The population to select from.
        :param int population_size: The size of the population to select.
        :return List[GeneticCandidate]: The selected population.
        """
        if len(population) <= population_size:
            return population
        fitness = numpy.array([c.fitness for c in population], dtype=float)
        array = numpy.empty(len(population), dtype=GeneticCandidate)
        array[:] = population[:]
        sum_fitness = sum(fitness)
        if sum_fitness <= EPSILON:
            return random.sample(population, k=population_size)
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
        """
        Select a population from the given population using the tournament selection method.
        :param List[GeneticCandidate] population: The population to select from.
        :param int population_size: The size of the population to select.
        :return List[GeneticCandidate]: The selected population.
        """
        if len(population) <= population_size:
            return population
        population = population[:]
        candidates = list()
        for _ in range(population_size):
            tournament = random.sample(population, k=self.tournament_size)
            fitness = numpy.array([c.fitness for c in tournament], dtype=float)
            array = numpy.empty(len(tournament), dtype=GeneticCandidate)
            array[:] = tournament[:]
            sum_fitness = sum(fitness)
            if sum_fitness <= EPSILON:
                choice = random.choice(array)
            else:
                choice = numpy.random.choice(
                    array,
                    size=1,
                    p=fitness / sum(fitness),
                )[0]
            candidates.append(choice)
            population.remove(choice)
        return candidates


__all__ = ["Selection", "RandomSelection", "UniversalSelection", "TournamentSelection"]
