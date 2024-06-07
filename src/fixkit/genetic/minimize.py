"""
The minimize module provides the necessary tools to minimize a candidate.
"""

import abc
from typing import List, Optional

from fixkit.candidate import Candidate, GeneticCandidate
from fixkit.fitness.engine import Engine


class Minimizer(abc.ABC):
    """
    Abstract class for minimization operators.
    """

    @abc.abstractmethod
    def minimize(self, population: List[Candidate]) -> List[Candidate]:
        """
        Abstract method for minimizing a population of candidates.
        :param List[Candidate] population: The population to minimize.
        :return List[Candidate]: The minimized population.
        """
        pass

    @abc.abstractmethod
    def minimize_candidate(self, candidate: Candidate) -> Candidate:
        """
        Abstract method for minimizing a candidate.
        :param Candidate candidate: The candidate to minimize.
        :return Candidate: The minimized candidate.
        """
        pass


class MutationMinimizer(Minimizer, abc.ABC):
    """
    Abstract class for mutation minimization operators.
    """

    def __init__(self, fitness: Optional[Engine] = None):
        """
        Initialize the minimizer with a fitness engine.
        :param Optional[Engine] fitness: The fitness engine to use for evaluating the fitness of a candidate.
        If not set during initialization, it needs to be set afterward.
        """
        self.fitness = fitness

    def minimize(self, population: List[GeneticCandidate]) -> List[GeneticCandidate]:
        """
        Minimize a population of candidates by minimizing each candidate.
        :param List[GeneticCandidate] population: The population to minimize.
        :return List[GeneticCandidate]: The minimized population.
        """
        return [self.minimize_candidate(candidate) for candidate in population]


class DefaultMutationMinimizer(MutationMinimizer):
    def minimize(self, population: List[GeneticCandidate]) -> List[GeneticCandidate]:
        """
        Minimize a population of candidates by not minimizing them.
        :param List[GeneticCandidate] population: The population to minimize.
        :return List[GeneticCandidate]: The minimized population.
        """
        return population

    def minimize_candidate(self, candidate: GeneticCandidate) -> GeneticCandidate:
        """
        Minimize a candidate to remove redundant mutations by not minimizing it.
        :param GeneticCandidate candidate: The candidate to minimize.
        :return GeneticCandidate: The minimized candidate.
        """
        return candidate


class DDMutationMinimizer(MutationMinimizer):
    def minimize_candidate(self, candidate: GeneticCandidate) -> GeneticCandidate:
        """
        Minimize a candidate to remove redundant mutations using delta debugging.
        :param GeneticCandidate candidate: The candidate to minimize.
        :return GeneticCandidate: The minimized candidate.
        """
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


__all__ = [
    "Minimizer",
    "MutationMinimizer",
    "DefaultMutationMinimizer",
    "DDMutationMinimizer",
]
