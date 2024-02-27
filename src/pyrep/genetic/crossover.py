import abc
import random
from typing import Optional, Tuple

from pyrep.candidate import GeneticCandidate


class Crossover(abc.ABC):
    @abc.abstractmethod
    def crossover(
        self, parent_x: GeneticCandidate, parent_y: GeneticCandidate
    ) -> Optional[Tuple[GeneticCandidate, GeneticCandidate]]:
        pass


class OnePointCrossover(Crossover):
    def crossover(
        self, parent_x: GeneticCandidate, parent_y: GeneticCandidate
    ) -> Optional[Tuple[GeneticCandidate, GeneticCandidate]]:
        index_x = random.randint(0, len(parent_x))
        index_y = random.randint(0, len(parent_y))

        ax, bx = parent_x[:index_x], parent_x[index_x:]
        ay, by = parent_y[:index_y], parent_y[index_y:]

        return GeneticCandidate(
            parent_x.src, mutations=ax + by, gen=parent_x.gen + 1
        ), GeneticCandidate(parent_y.src, mutations=ay + bx, gen=parent_y.gen + 1)
