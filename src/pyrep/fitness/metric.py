"""
The fitness module provides the necessary tools to evaluate the fitness of a candidate.
"""

import abc
import json
import os
import subprocess
from pathlib import Path
from typing import Set, Dict, Optional, Tuple


class Fitness(abc.ABC):
    """
    Abstract class for fitness functions.
    """

    def __init__(self, passing: Set[str], failing: Set[str], timeout: int = 10):
        """
        Initialize the fitness function.
        :param Set[str] passing: The set of passing tests.
        :param Set[str] failing: The set of failing tests.
        :param int timeout: The timeout for running the fitness function.
        """
        self.passing = passing
        self.failing = failing
        self.timeout = timeout

    def run(
        self, cwd: os.PathLike, env: Optional[Dict[str, str]] = None
    ) -> Tuple[Set[str], Set[str]]:
        """
        Run the tests in the directory given by cwd with the provided environment and return the passing and failing
        tests.
        :param os.PathLike cwd: The directory to run the tests in.
        :param Optional[Dict[str,str]] env: The environment to run the tests in.
        :return Tuple[Set[str], Set[str]]: A tuple of the passing and failing tests.
        """
        tests = list(self.passing | self.failing)
        print(tests)
        try:
            # Run the tests and get the results.
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "--json-report",
                ]
                + tests,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout,
            )
            # Parse the results and return the passing and failing tests.
            passing = set()
            failing = set()
            cwd = Path(cwd)
            with open(cwd / ".report.json") as fp:
                results = json.load(fp)
            print(results)
            for result in results["tests"]:
                if result["outcome"] == "passed":
                    passing.add(result["nodeid"])
                else:
                    failing.add(result["nodeid"])
            print(passing)
            print(failing)
            return passing, failing
        except subprocess.TimeoutExpired:
            return set(), set()

    def evaluate_fitness(
        self, cwd: os.PathLike, env: Optional[Dict[str, str]] = None
    ) -> float:
        """
        Abstract method to evaluate the fitness of a candidate in the directory given by cwd with the provided
        :param os.PathLike cwd: The directory to evaluate the fitness in.
        :param Optional[Dict[str, str]] env: The environment to evaluate the fitness in.
        :return float: The fitness of the candidate in the directory.
        """
        passing, failing = self.run(cwd, env)
        return self.fitness(passing, failing)

    @abc.abstractmethod
    def fitness(self, passing: Set[str], failing: Set[str]) -> float:
        """
        Abstract method to evaluate the fitness of a candidate in the directory given by cwd with the provided
        :param Set[str] passing: The set of passing tests.
        :param Set[str] failing: The set of failing tests.
        :return float: The fitness of the candidate based on the sets of passing and failing tests.
        """
        pass


class GenProgFitness(Fitness):
    def __init__(
        self,
        passing: Set[str],
        failing: Set[str],
        w_pos_t: float = 1,
        w_neg_t: float = 10,
        timeout: int = 10,
    ):
        """
        Initialize the GenProg fitness function.
        :param Set[str] passing: The set of passing tests.
        :param Set[str] failing: The set of failing tests.
        :param float w_pos_t: The weight for the passing tests if passed.
        :param float w_neg_t: The weight for the failing tests if passed.
        :param int timeout: The timeout for running the fitness function.
        """
        super().__init__(passing, failing, timeout=timeout)
        self.w_pos_t = w_pos_t
        self.w_neg_t = w_neg_t

    def fitness(self, passing: Set[str], failing: Set[str]) -> float:
        """
        Evaluate the fitness of a candidate in the directory given by cwd with the provided environment based on the
        GenProg fitness w_pos_t * |{t in passing tests | C passes t}| + w_neg_t * |{t in failing tests | C passes t}|.
        :param Set[str] passing: The set of passing tests.
        :param Set[str] failing: The set of failing tests.
        :return float: The fitness of the candidate based on the sets of passing and failing tests.
        """
        return (
            self.w_pos_t * len(passing & self.passing)
            + self.w_neg_t * len(passing & self.failing)
        ) / (self.w_pos_t * len(self.passing) + self.w_neg_t * len(self.failing))


__all__ = ["Fitness", "GenProgFitness"]
