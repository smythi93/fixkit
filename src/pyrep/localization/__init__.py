import abc
import math
import os
from pathlib import Path
from typing import List, Dict, Optional

from sflkit import Predicate
from sflkit.analysis.suggestion import Location

from pyrep.constants import DEFAULT_WORK_DIR


class WeightedLocation(Location):
    def __init__(self, file: str, line: int, weight: float):
        super().__init__(file, line)
        self.weight = 0 if math.isnan(weight) else weight


class LocalizationError(RuntimeError):
    pass


class Localization:
    def __init__(
        self,
        src: os.PathLike,
        failing: Optional[List[str]] = None,
        passing: Optional[List[str]] = None,
        tests: Optional[List[str]] = None,
        out: Optional[os.PathLike] = None,
        env: Optional[Dict[str, str]] = None,
        metric: Optional[str] = None,
    ):
        self.src = Path(src) if src else None
        self.failing = failing
        self.passing = passing
        self.tests = tests
        self.out = Path(out) if out else DEFAULT_WORK_DIR / "localization"
        self.prepared = False
        self.env = env or os.environ
        self.metric = None
        self.set_metric(metric)

    def set_metric(self, metric: str):
        self.metric = getattr(Predicate, metric)

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
        if self.prepared:
            return sorted(self.get_suggestions(), key=lambda x: x.weight, reverse=True)
        else:
            raise LocalizationError("Localization not prepared")
