"""
The engine module provides the necessary tools to evaluate the fitness of a candidate in parallel.
"""

import os
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from typing import List, Tuple, Dict

import tests4py.api as t4p
from tests4py.tests.utils import TestResult

from pyrep.candidate import GeneticCandidate
from pyrep.constants import DEFAULT_WORK_DIR, XML_OUTPUT
from pyrep.fitness.metric import Fitness
from pyrep.genetic.operators import MutationOperator
from pyrep.genetic.transform import MutationTransformer


class Worker:
    """
    Worker class to evaluate the fitness of a candidate.
    """

    def __init__(
        self,
        identifier: str,
        pre_calculated: Dict[Tuple[MutationOperator], float],
        out: os.PathLike = None,
    ):
        """
        Initialize the worker.
        :param str identifier: The identifier of the worker. Is used to create a directory for the worker.
        :param Dict[Tuple[MutationOperator], float] pre_calculated: The pre-calculated fitness values shared between
        all workers.
        :param os.PathLike out: The output directory for the worker.
        """
        self.identifier = identifier
        self.pre_calculated = pre_calculated
        self.out = Path(out or DEFAULT_WORK_DIR)
        self.cwd = self.out / identifier
        self.transformer = MutationTransformer()

    def evaluate(self, candidate: GeneticCandidate, fitness: Fitness):
        """
        Evaluate the fitness of a candidate by checking the pre-calculated fitness, otherwise run the fitness on the
        candidate.
        :param GeneticCandidate candidate: The candidate to evaluate.
        :param Fitness fitness: The fitness function to use.
        """
        key = tuple(candidate.mutations)
        if key in self.pre_calculated:
            candidate.fitness = self.pre_calculated[key]
        else:
            self.transformer.transform(candidate, self.cwd)
            candidate.fitness = fitness.evaluate_fitness(self.cwd)
            self.pre_calculated[key] = candidate.fitness

    def run(self, candidates: Queue[GeneticCandidate], fitness: Fitness):
        """
        Run the worker on the shared queue of candidates.
        :param Queue[GeneticCandidate] candidates: The shared queue of candidates.
        :param Fitness fitness: The fitness function to use.
        :return:
        """
        try:
            while True:
                self.evaluate(candidates.get_nowait(), fitness)
        except Empty:
            pass


class Engine:
    """
    Engine class to evaluate the fitness of a list of candidates in parallel.
    """

    def __init__(
        self,
        fitness: Fitness,
        workers: int = 1,
        out: os.PathLike = None,
    ):
        """
        Initialize the engine.
        :param Fitness fitness: The fitness function to use.
        :param int workers: The number of workers to use.
        :param os.PathLike out: The output directory for the workers.
        """
        self.fitness = fitness
        self.out = Path(out or DEFAULT_WORK_DIR)
        self.pre_calculated = dict()
        self.workers = [
            Worker(f"rep_{i}", self.pre_calculated, self.out) for i in range(workers)
        ]

    def evaluate(self, candidates=List[GeneticCandidate]):
        """
        Evaluate the fitness of a list of candidates in parallel.
        :param List[GeneticCandidate] candidates: The list of candidates to evaluate.
        """
        threads = []
        data = Queue()
        for candidate in candidates:
            data.put(candidate)
        for worker in self.workers:
            thread = Thread(target=worker.run, args=(data, self.fitness))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()


class Tests4PyWorker(Worker):
    """
    Worker class to evaluate the fitness of a candidate using Tests4Py.
    """

    def evaluate(self, candidate: GeneticCandidate, fitness: Fitness):
        """
        Evaluate the fitness of a candidate using Tests4Py.
        :param GeneticCandidate candidate: The candidate to evaluate.
        :param Fitness fitness: The fitness function to use.
        """
        key = tuple(candidate.mutations)
        if key in self.pre_calculated:
            candidate.fitness = self.pre_calculated[key]
        else:
            self.transformer.transform(candidate, self.cwd)
            report = t4p.build(self.cwd)
            if report.raised:
                candidate.fitness = 0
            else:
                report = t4p.test(
                    self.cwd,
                    relevant_tests=True,
                    xml_output=XML_OUTPUT(self.identifier),
                )
                if report.raised:
                    candidate.fitness = 0
                else:
                    passing, failing = set(), set()
                    for test, result in report.results:
                        if result == TestResult.PASSING:
                            passing.add(test)
                        elif result == TestResult.FAILING:
                            failing.add(test)
                    candidate.fitness = fitness.fitness(passing, failing)
            self.pre_calculated[key] = candidate.fitness


class Tests4PyEngine(Engine):
    """
    Engine class to evaluate the fitness of a list of candidates in parallel using Tests4Py.
    """

    def __init__(
        self,
        fitness: Fitness,
        workers: int = 1,
        out: os.PathLike = None,
    ):
        """
        Initialize the engine.
        :param Fitness fitness: The fitness function to use.
        :param int workers: The number of workers to use.
        :param os.PathLike out: The output directory for the workers.
        """
        super().__init__(fitness, workers, out)
        self.workers = [
            Tests4PyWorker(f"rep_{i}", self.pre_calculated, self.out)
            for i in range(workers)
        ]


__all__ = ["Engine"]
