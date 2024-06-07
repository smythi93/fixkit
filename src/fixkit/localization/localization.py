"""
The localization module provides the necessary tools to localize a fault.
"""

import abc
import os
from pathlib import Path
from typing import List, Dict, Optional

from sflkit import Predicate

from fixkit.constants import DEFAULT_WORK_DIR
from fixkit.localization.location import WeightedLocation


class LocalizationError(RuntimeError):
    """
    Error raised when an error occurs during localization.
    """

    pass


class Localization(abc.ABC):
    """
    Abstract class for localizing a fault.
    """

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
        """
        Initialize the localization.
        :param os.PathLike src: The source directory of the project.
        :param Optional[List[str]] failing: The set of failing tests, will override tests.
        :param Optional[List[str]] passing: The set of passing tests, will override tests.
        :param Optional[List[str]] tests: The set of all tests, as an alternative when an oracle exists.
        :param Optional[os.PathLike] out: The output directory for the localization.
        :param Optional[Dict[str, str]] env: The environment to run the tests in.
        :param Optional[str] metric: The metric to use for the localization.
        """
        self.src = Path(src) if src else None
        self.failing = set(failing or [])
        self.passing = set(passing or [])
        self.tests = set(tests or [])
        self.out = Path(out or DEFAULT_WORK_DIR, "localization")
        self.prepared = False
        self.env = env or os.environ
        self.metric = None
        self.set_metric(metric)

    def set_metric(self, metric: str):
        """
        Set the metric to use for the localization.
        :param str metric: The metric to use.
        """
        self.metric = getattr(Predicate, metric)

    def prepare(self):
        """
        Prepare the localization.
        """
        if not self.prepared:
            self.run_preparation()
            self.prepared = True

    @abc.abstractmethod
    def run_preparation(self):
        """
        Abstract method for running the preparation of the localization.
        """
        pass

    @abc.abstractmethod
    def get_suggestions(self) -> List[WeightedLocation]:
        """
        Abstract method for getting the suggestions of the localization.
        :return List[WeightedLocation]: The list of weighted locations.
        """
        pass

    def get_sorted_suggestions(self) -> List[WeightedLocation]:
        """
        Get the sorted suggestions of the localization.
        :return List[WeightedLocation]: The sorted list of weighted locations.
        """
        if self.prepared:
            return sorted(self.get_suggestions(), reverse=True)
        else:
            raise LocalizationError("Localization not prepared")


__all__ = ["Localization", "LocalizationError"]
