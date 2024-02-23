import abc
import random
from typing import Optional, Tuple

from pyrep.candidate import Candidate


class Crossover(abc.ABC):
    @abc.abstractmethod
    def crossover(
        self, parent_x: Candidate, parent_y: Candidate
    ) -> Optional[Tuple[Candidate, Candidate]]:
        pass


class OnePointCrossover(Crossover):
    def crossover(
        self, parent_x: Candidate, parent_y: Candidate
    ) -> Optional[Tuple[Candidate, Candidate]]:
        index_x = random.randint(0, len(parent_x))
        index_y = random.randint(0, len(parent_y))

        ax, bx = parent_x[:index_x], parent_x[index_x:]
        ay, by = parent_y[:index_y], parent_y[index_y:]

        return Candidate(
            parent_x.src, mutations=ax + by, gen=parent_x.gen + 1
        ), Candidate(parent_y.src, mutations=ay + bx, gen=parent_y.gen + 1)
