"""
The crossover module provides the necessary tools to perform crossover operations on candidates.
"""

import abc
import random
from typing import Optional, Tuple

from fixkit.candidate import GeneticCandidate


class Crossover(abc.ABC):
    """
    Abstract class for crossover operators.
    """

    @abc.abstractmethod
    def crossover(
        self, parent_x: GeneticCandidate, parent_y: GeneticCandidate
    ) -> Optional[Tuple[GeneticCandidate, GeneticCandidate]]:
        """
        Abstract method for crossover operation.
        :param GeneticCandidate parent_x: The first parent to perform the crossover.
        :param GeneticCandidate parent_y: The second parent to perform the crossover.
        :return Optional[Tuple[GeneticCandidate, GeneticCandidate]]: A tuple of the two offspring of the parents if
        they exist.
        """
        pass


class OnePointCrossover(Crossover):
    """
    One-point crossover operator.
    """

    def crossover(
        self, parent_x: GeneticCandidate, parent_y: GeneticCandidate
    ) -> Optional[Tuple[GeneticCandidate, GeneticCandidate]]:
        """
        Perform one-point crossover on the two parents by selecting an index and create two new mutation lists.
        :param GeneticCandidate parent_x: The first parent to perform the crossover.
        :param GeneticCandidate parent_y: The second parent to perform the crossover.
        :return Optional[Tuple[GeneticCandidate, GeneticCandidate]]: A tuple of the two offspring of the parents if
        they exist.
        """
        index_x = random.randint(0, len(parent_x))
        index_y = random.randint(0, len(parent_y))

        ax, bx = parent_x[:index_x], parent_x[index_x:]
        ay, by = parent_y[:index_y], parent_y[index_y:]

        return parent_x.offspring(mutations=ax + by), parent_y.offspring(
            mutations=ay + bx
        )


__all__ = ["Crossover", "OnePointCrossover"]
