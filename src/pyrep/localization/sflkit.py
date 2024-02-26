import os
from pathlib import Path
from typing import List, Optional, Dict

import sflkit
from sflkit import Config

from pyrep.constants import DEFAULT_EXCLUDES, SFLKIT_EVENTS_PATH
from pyrep.localization import Localization, WeightedLocation


class SFLKitLocalization(Localization):
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
        if passing is None:
            return events_path or SFLKIT_EVENTS_PATH
        else:
            return (events_path or SFLKIT_EVENTS_PATH) / (
                "passing" if passing else "failing"
            )

    def run_preparation(self):
        sflkit.instrument_config(self.config)
        passing_failing = (self.passing or set()) | (self.failing or set())
        tests = passing_failing or self.tests or {"tests"}
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
        self.analyzer = sflkit.Analyzer(
            self.config.failing, self.config.passing, self.config.factory
        )
        self.analyzer.analyze()

    def get_suggestions(self):
        return [
            WeightedLocation(
                file=loc.file, line=loc.line, weight=suggestion.suspiciousness
            )
            for suggestion in self.analyzer.get_sorted_suggestions(
                self.src, self.metric
            )
            for loc in suggestion.lines
        ]
