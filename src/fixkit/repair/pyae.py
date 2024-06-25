import abc
import ast
import os
from typing import List, Optional, Generator, Set, Tuple, Dict

# noinspection PyPackageRequirements
from tests4py.tests.utils import TestResult

from fixkit.analysis.dataflow import DataflowAnalysis
from fixkit.candidate import GeneticCandidate, Candidate
from fixkit.fitness.metric import AbsoluteFitness
from fixkit.genetic.operators import (
    Delete,
    InsertBefore,
    InsertAfter,
    MutationOperator,
    Insert,
)
from fixkit.genetic.types import Population
from fixkit.localization.localization import Localization
from fixkit.localization.location import WeightedLocation
from fixkit.localization.normalization import normalize
from fixkit.logger import LOGGER
from fixkit.repair.repair import GeneticRepair


class AbstractAE(GeneticRepair, abc.ABC):
    def __init__(
        self,
        src: os.PathLike,
        localization: Localization,
        k: int = 1,
        out: os.PathLike = None,
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
        excludes: Optional[List[str]] = None,
    ):
        self.metric = AbsoluteFitness(set(), set())
        self.k = k
        self.tests: Set[str] = []
        super().__init__(
            src=src,
            fitness=None,
            localization=localization,
            population_size=1,
            max_generations=1,
            operators=[Delete, InsertAfter, InsertBefore],
            selection=None,
            crossover_operator=None,
            minimizer=None,
            workers=1,
            out=out,
            is_t4p=is_t4p,
            is_system_test=is_system_test,
            system_tests=system_tests,
            line_mode=line_mode,
            w_mut=1,
            serial=True,
            excludes=excludes,
        )

    @classmethod
    @abc.abstractmethod
    def _from_source(
        cls,
        src: os.PathLike,
        excludes: Optional[List[str]],
        localization: Localization,
        k: int = 1,
        out: os.PathLike = None,
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
    ) -> GeneticRepair:
        return NotImplemented

    @classmethod
    def from_source(cls, src: os.PathLike, *args, **kwargs) -> "GeneticRepair":
        return cls._from_source(src, *args, **kwargs)

    def prepare_repair(self) -> Population:
        # Localize the faults.
        LOGGER.info("Localizing the faulty code locations.")
        suggestions = self.localize()
        normalize(suggestions)
        self.set_suggestions(suggestions)

    @abc.abstractmethod
    def equivalent(self, candidate_1: GeneticCandidate, candidate_2: GeneticCandidate):
        pass

    @abc.abstractmethod
    def repair_strategy(self, model) -> Generator[MutationOperator, None, None]:
        pass

    @abc.abstractmethod
    def test_strategy(self, model) -> Generator[str, None, None]:
        pass

    def localize(self) -> List[WeightedLocation]:
        locations = super().localize()
        self.tests = list(self.localization.failing)
        self.tests += list(self.localization.passing)
        return locations

    def candidate_repairs(self, model) -> Generator[List[Candidate], None, None]:
        for i in range(1, self.k + 1):
            generators = [self.repair_strategy(model) for _ in range(i)]
            current_state = [next(generator) for generator in generators]
            yield self.initial_candidate.offspring(current_state[:])
            current = 0
            while current < len(generators):
                try:
                    current_state[current] = next(generators[current])
                    current = max(0, current - 1)
                    yield self.initial_candidate.offspring(current_state[:])
                except StopIteration:
                    generators[current] = self.repair_strategy(model)
                    current += 1

    def repair_loop(self):
        model: Set[Tuple[GeneticCandidate, str, TestResult]] = set()
        equivalent_classes = set()
        for candidate in self.candidate_repairs(model):
            if not (any(self.equivalent(candidate, c) for c in equivalent_classes)):
                equivalent_classes.add(candidate)
                passing = True
                for test, result in self.fitness.evaluate_sequentially(
                    candidate, self.test_strategy(model)
                ):
                    if test != "build":
                        model.add((candidate, test, result))
                    if result != TestResult.PASSING:
                        passing = False
                        break
                if passing:
                    self.population = [candidate]
                    return
        self.population = []


class PyAE(AbstractAE):
    def __init__(
        self,
        src: os.PathLike,
        localization: Localization,
        k: int = 1,
        out: os.PathLike = None,
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
        excludes: Optional[List[str]] = None,
    ):
        super().__init__(
            src=src,
            localization=localization,
            k=k,
            out=out,
            is_t4p=is_t4p,
            is_system_test=is_system_test,
            system_tests=system_tests,
            line_mode=line_mode,
            excludes=excludes,
        )
        self.dataflow_analysis = DataflowAnalysis()

    def repair_strategy(self, model) -> Generator[MutationOperator, None, None]:
        reversed_suggestions = [location.identifier for location in self.suggestions]
        for identifier in self.choices:
            if identifier not in reversed_suggestions:
                reversed_suggestions.append(identifier)
        reversed_suggestions = reversed(reversed_suggestions)
        for location in self.suggestions:
            yield Delete(identifier=location.identifier)
            for identifier in reversed_suggestions:
                yield InsertBefore(identifier=location.identifier, choices=[identifier])
                yield InsertAfter(identifier=location.identifier, choices=[identifier])

    def test_strategy(self, model) -> Generator[str, None, None]:
        tests = {test: 0 for test in self.tests}
        for candidate, test, result in model:
            if result == TestResult.FAILING:
                tests[test] += 1
        tests = sorted(tests.items(), key=lambda x: x[1], reverse=True)
        for test, _ in tests:
            yield test

    def equivalent(self, candidate_1: GeneticCandidate, candidate_2: GeneticCandidate):
        return candidate_1 == candidate_2

    # noinspection PyUnusedLocal
    @staticmethod
    def syntactic_equivalent(
        files: Set[str],
        candidate_1: GeneticCandidate,
        candidate_2: GeneticCandidate,
        asts_1: Dict[str, ast.AST],
        asts_2: Dict[str, ast.AST],
    ):
        for file in files:
            if (
                file not in asts_1
                or file not in asts_2
                or ast.dump(asts_1[file]) != ast.dump(asts_2[file])
            ):
                return False
        return True

    @staticmethod
    def dead_code_equivalent(
        files: Set[str],
        candidate_1: GeneticCandidate,
        candidate_2: GeneticCandidate,
        asts_1: Dict[str, ast.AST],
        asts_2: Dict[str, ast.AST],
    ):
        insertions_1: Set[Insert] = set()
        insertions_2: Set[Insert] = set()
        deletion_1: Set[Delete] = set()
        deletion_2: Set[Delete] = set()
        for operator in candidate_1.mutations:
            if isinstance(operator, Insert):
                insertions_1.add(operator.identifier)
            elif isinstance(operator, Delete):
                deletion_1.add(operator)
        for operator in candidate_2.mutations:
            if isinstance(operator, Insert):
                insertions_2.add(operator.identifier)
            elif isinstance(operator, Delete):
                deletion_2.add(operator)
        if deletion_1 != deletion_2:
            return False
        insertions_1 = insertions_1.difference(insertions_2)
        insertions_2 = insertions_2.difference(insertions_1)
        if insertions_1 == insertions_2:
            return True

        for file in files:
            if file not in asts_1 or file not in asts_2:
                return False

        return False

    @staticmethod
    def order_equivalent(
        files: Set[str],
        candidate_1: GeneticCandidate,
        candidate_2: GeneticCandidate,
        asts_1: Dict[str, ast.AST],
        asts_2: Dict[str, ast.AST],
    ):
        insertions_1: Set[Insert] = set()
        insertions_2: Set[Insert] = set()
        for operator in candidate_1.mutations:
            if isinstance(operator, Insert):
                insertions_1.add(operator.identifier)
        for operator in candidate_2.mutations:
            if isinstance(operator, Insert):
                insertions_2.add(operator.identifier)
        insertions_1 = insertions_1.difference(insertions_2)
        insertions_2 = insertions_2.difference(insertions_1)
        if insertions_1 == insertions_2:
            return True

        for file in files:
            if file not in asts_1 or file not in asts_2:
                return False

        return False

    @classmethod
    def _from_source(
        cls,
        src: os.PathLike,
        excludes: Optional[List[str]],
        localization: Localization,
        k: int = 1,
        out: os.PathLike = None,
        is_t4p: bool = False,
        is_system_test: bool = False,
        system_tests: Optional[os.PathLike | List[os.PathLike]] = None,
        line_mode: bool = False,
    ) -> GeneticRepair:
        return PyAE(
            src=src,
            localization=localization,
            k=k,
            out=out,
            is_t4p=is_t4p,
            is_system_test=is_system_test,
            system_tests=system_tests,
            line_mode=line_mode,
            excludes=excludes,
        )
