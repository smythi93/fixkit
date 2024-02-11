import abc
import os
from pathlib import Path
from typing import List

from sflkit.analysis.suggestion import Location

from pyrep.constants import DEFAULT_WORK_DIR


class WeightedLocation(Location):
    def __init__(self, file: str, line: int, weight: float):
        super().__init__(file, line)
        self.weight = weight


class Localization:
    def __init__(
        self,
        src: os.PathLike,
        failing: List[str] = None,
        passing: List[str] = None,
        tests: List[str] = None,
        out: os.PathLike = None,
    ):
        self.src = Path(src) if src else None
        self.failing = failing
        self.passing = passing
        self.tests = tests
        self.out = Path(out) if out else DEFAULT_WORK_DIR / "localization"
        self.prepared = False

    def prepare(self):
        if not self.prepared:
            self.run_preparation()
            self.prepared = True

    @abc.abstractmethod
    def run_preparation(self):
        pass

    def get_suggestions(self) -> List[WeightedLocation]:
        pass

    def get_sorted_suggestions(self) -> List[WeightedLocation]:
        return sorted(self.get_suggestions(), key=lambda x: x.weight, reverse=True)
