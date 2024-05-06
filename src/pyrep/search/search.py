import abc
from typing import List, Callable, Optional, Type

from pyrep.candidate import GeneticCandidate
from pyrep.genetic.operators import MutationOperator
from pyrep.genetic.types import GeneticFunction, Population
from pyrep.localization.location import WeightedIdentifier
from pyrep.logger import LOGGER


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
        mutators: List[Type[MutationOperator]], #Auch Callable?
        suggestions: List[WeightedIdentifier], #Callable die suggestions returnt .. da diese sich ja ändern ??
        choices: Optional[List[int]] = None, # sollten die nicht optional sein? bei mutation operator sind sie auch optional
        mutate: Optional[GeneticFunction] = None,
    ):
        super().__init__()
        self.mutators = mutators
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
        #TODO: erklären lassen [:] -> copy aber wieso 2 mal
        population = population[:]
        for candidate in population[:]:
            for location in self.suggestions:
                if location.weight > 0:
                    for mutatator in self.mutators:
                        new_candidate = candidate.clone()
                        new_candidate.mutations.append(
                            mutatator(location.identifier, self.choices)
                        )
                        population.append(new_candidate)
        return population
