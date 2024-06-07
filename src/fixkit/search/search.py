import abc
from typing import List, Callable, Optional, Type

from fixkit.candidate import GeneticCandidate
from fixkit.genetic.operators import MutationOperator
from fixkit.genetic.types import GeneticFunction, Population
from fixkit.localization.location import WeightedIdentifier
from fixkit.logger import LOGGER


class SearchStrategy(abc.ABC):
    def search(self, population: List[GeneticCandidate]) -> List[GeneticCandidate]:
        pass


class EvolutionaryStrategy(SearchStrategy):
    def __init__(
        self,
        viable: GeneticFunction,
        select: GeneticFunction,
        crossover: GeneticFunction,
        mutate: GeneticFunction,
    ):
        super().__init__()
        self.viable: GeneticFunction = viable
        self.select: GeneticFunction = select
        self.crossover: GeneticFunction = crossover
        self.mutate: GeneticFunction = mutate

    def search(self, population: List[GeneticCandidate]) -> List[GeneticCandidate]:
        # Filter the population and select the best candidates.
        LOGGER.info("Filtering the population and selecting the best candidates.")
        population = self.viable(population)
        population = self.select(population)

        # Crossover and mutate the population.
        LOGGER.info("Crossover the population.")
        population = self.crossover(population)
        LOGGER.info("Mutate the population.")
        return self.mutate(population)


class ExhaustiveStrategy(SearchStrategy):
    def __init__(
        self,
        operators: List[Type[MutationOperator]], #Auch Callable?
        suggestions: List[WeightedIdentifier], #Callable oder im constructor garantieren das suggestions vorher calculated werden
        choices: Optional[List[int]] = None,
        mutate: Optional[GeneticFunction] = None,
    ):
        super().__init__()
        self.operators = operators
        self.suggestions: List[WeightedIdentifier] = suggestions
        self.choices = choices
        self.mutate: GeneticFunction = mutate or self._mutate

    def search(self, population: Population) -> Population:
        return self.mutate(population)

    def _mutate(self, population: Population) -> Population:
        """
        Mutate a population to create a new population.
        :param GeneticCandidate population: The population to mutate.
        :return GeneticCandidate: The new mutated population.
        """
        #TODO: Wieso [:], da wir ja candidate clonen
        LOGGER.info("In Exhaustive Search")
        population = population[:]
        for candidate in population[:]:
            for location in self.suggestions:
                if location.weight > 0:
                    for operator in self.operators:
                        new_candidate = candidate.clone()
                        #location gat kein identifier aber ein .line
                        new_candidate.mutations.append(
                            operator(location.line, self.choices)
                        )
                        population.append(new_candidate)
        return population
