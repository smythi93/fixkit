from typing import Callable, List

from fixkit.candidate import GeneticCandidate

Population = List[GeneticCandidate]
GeneticFunction = Callable[[Population], Population]
