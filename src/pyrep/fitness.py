import abc
import json
import os
import subprocess
from pathlib import Path
from typing import Set, Dict, Optional, Tuple


class Fitness(abc.ABC):
    def __init__(self, passing: Set[str], failing: Set[str]):
        self.passing = passing
        self.failing = failing

    def run(
        self, cwd: os.PathLike, env: Optional[Dict[str, str]] = None
    ) -> Tuple[Set[str], Set[str]]:
        tests = list(self.passing | self.failing)
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
        )
        passing = set()
        failing = set()
        cwd = Path(cwd)
        with open(cwd / ".report.json") as fp:
            results = json.load(fp)
        for result in results["tests"]:
            if result["outcome"] == "passed":
                passing.add(result["nodeid"])
            else:
                failing.add(result["nodeid"])
        return passing, failing

    @abc.abstractmethod
    def fitness(self, cwd: os.PathLike, env: Optional[Dict[str, str]] = None) -> float:
        pass


class GenProgFitness(Fitness):
    def __init__(
        self,
        passing: Set[str],
        failing: Set[str],
        w_pos_t: float = 1,
        w_neg_t: float = 10,
    ):
        super().__init__(passing, failing)
        self.w_pos_t = w_pos_t
        self.w_neg_t = w_neg_t

    def fitness(self, cwd: os.PathLike, env: Optional[Dict[str, str]] = None) -> float:
        passing, _ = self.run(cwd, env)
        return self.w_pos_t * len(passing & self.passing) - self.w_neg_t * len(
            passing & self.failing
        )
