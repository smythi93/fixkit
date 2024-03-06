"""
The sflkit module provides the necessary tools to localize a fault using SFLKit.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict

import sflkit
from sflkit import Config

from pyrep.constants import DEFAULT_EXCLUDES, SFLKIT_EVENTS_PATH
from pyrep.localization.localization import Localization
from pyrep.localization.location import WeightedLocation


class SFLKitLocalization(Localization):
    """
    Class for localizing a fault using SFLKit.
    """

    def __init__(
        self,
        src: os.PathLike,
        failing: Optional[List[str]] = None,
        passing: Optional[List[str]] = None,
        tests: Optional[List[str]] = None,
        out: Optional[os.PathLike] = None,
        env: Optional[Dict[str, str]] = None,
        events: Optional[List[str]] = None,
        predicates: Optional[List[str]] = None,
        metric: Optional[str] = None,
        events_path: Optional[os.PathLike] = None,
        included_files: Optional[List[str]] = None,
        excluded_files: Optional[List[str]] = None,
        test_base: Optional[os.PathLike] = None,
    ):
        """
        Initialize the SFLKit localization.
        :param os.PathLike src: The source directory of the project.
        :param Optional[List[str]] failing: The set of failing tests, will override tests.
        :param Optional[List[str]] passing: The set of passing tests, will override tests.
        :param Optional[List[str]] tests: The set of all tests, as an alternative when an oracle exists.
        :param Optional[os.PathLike] out: The output directory for the localization.
        :param Optional[Dict[str, str]] env: The environment to run the tests in.
        :param Optional[List[str]] events: The events to use for the localization.
        :param Optional[List[str]] predicates: The predicates to use for the localization.
        :param Optional[str] metric: The metric to use for the localization.
        :param Optional[os.PathLike] events_path: The path to the recorded events' path.
        :param Optional[List[str]] included_files: The files to include in the localization.
        :param Optional[List[str]] excluded_files: The files to exclude in the localization.
        :param Optional[os.PathLike] test_base: The base directory for the tests.
        """
        super().__init__(src, failing, passing, tests, out, env, metric)
        self.events = events
        self.predicates = predicates
        self.included_files = included_files or list()
        self.excluded_files = excluded_files or DEFAULT_EXCLUDES
        self.events_path = events_path
        self.test_base = test_base
        self.config = self.get_config()
        self.analyzer = None

    def get_config(
        self,
    ):
        """
        Get the SFLKit configuration for the localization.
        """
        return Config.create(
            path=str(self.src),
            language="python",
            events=",".join(self.events) if self.events else "line",
            metrics=self.metric.__name__,
            predicates=",".join(self.predicates) if self.predicates else "",
            passing=str(
                self.get_events_path(passing=True, events_path=self.events_path)
            ),
            failing=str(
                self.get_events_path(passing=False, events_path=self.events_path)
            ),
            working=str(self.out),
            include='"' + '","'.join(self.included_files) + '"',
            exclude='"' + '","'.join(self.excluded_files) + '"',
        )

    @staticmethod
    def get_events_path(
        passing: Optional[bool] = None, events_path: Optional[Path] = None
    ):
        """
        Get the path to the recorded events' path files.
        :param Optional[bool] passing: The type of events to get the path for.
        :param Optional[Path] events_path: The path to the recorded events' path.
        """
        if passing is None:
            return events_path or SFLKIT_EVENTS_PATH
        else:
            return (events_path or SFLKIT_EVENTS_PATH) / (
                "passing" if passing else "failing"
            )

    def run_preparation(self):
        """
        Run the preparation for the localization by executing the tests and collecting the events.
        """
        sflkit.instrument_config(self.config)
        # Get the passing and failing tests.
        passing_failing = (self.passing or set()) | (self.failing or set())
        tests = passing_failing or self.tests or {"tests"}
        # Run the tests and collect the events.
        runner = sflkit.runners.PytestRunner()
        runner.run(
            directory=self.out,
            output=self.get_events_path(events_path=self.events_path),
            files=list(tests),
            base=self.test_base,
            environ=self.env,
        )
        self.passing = set(runner.passing_tests)
        self.failing = set(runner.failing_tests)
        self.config = self.get_config()
        # Analyze the events.
        self.analyzer = sflkit.Analyzer(
            self.config.failing, self.config.passing, self.config.factory
        )
        self.analyzer.analyze()

    def get_suggestions(self) -> List[WeightedLocation]:
        """
        Get the suggestions of the localization by leveraging the analyzer.
        :return List[WeightedLocation]: The list of weighted locations.
        """
        return [
            WeightedLocation(
                file=loc.file, line=loc.line, weight=suggestion.suspiciousness
            )
            for suggestion in self.analyzer.get_sorted_suggestions(
                self.src, self.metric
            )
            for loc in suggestion.lines
        ]


__all__ = ["SFLKitLocalization"]
