from typing import Callable, List

from pyrep.candidate import GeneticCandidate

Population = List[GeneticCandidate]
GeneticFunction = Callable[[Population], Population]
