import os
from pathlib import Path
from typing import List, Optional

import sflkit
from sflkit import Config

from pyrep.constants import DEFAULT_EXCLUDES, SFLKIT_EVENTS_PATH
from pyrep.localization import Localization


class SFLKitLocalization(Localization):
    def __init__(
        self,
        src: os.PathLike,
        failing: List[str] = None,
        passing: List[str] = None,
        tests: List[str] = None,
        out: os.PathLike = None,
        events: List[str] = None,
        predicates: List[str] = None,
        metrics: List[str] = None,
        events_path: Optional[os.PathLike] = None,
        included_files: List[str] = None,
        excluded_files: List[str] = None,
        test_base: Optional[os.PathLike] = None,
    ):
        super().__init__(src, failing, passing, tests, out)
        if not included_files:
            included_files = list()
        if not excluded_files:
            excluded_files = DEFAULT_EXCLUDES
        self.events_path = events_path
        self.test_base = test_base
        self.config = Config.create(
            path=str(self.src),
            language="python",
            events=",".join(events) if events else "line",
            metrics=",".join(metrics) if metrics else "",
            predicates=",".join(predicates) if predicates else "",
            passing=str(self.get_events_path(passing=True, events_path=events_path)),
            failing=str(self.get_events_path(passing=False, events_path=events_path)),
            working=str(self.out),
            include='"' + '","'.join(included_files) + '"',
            exclude='"' + '","'.join(excluded_files) + '"',
        )
        self.analyzer = sflkit.Analyzer(
            self.config.failing, self.config.passing, self.config.factory
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
        passing_failing = (self.passing or list()) + (self.failing or list())
        tests = passing_failing or self.tests or Path("tests")
        sflkit.runners.PytestRunner().run(
            directory=self.out,
            output=self.get_events_path(events_path=self.events_path),
            files=tests,
            base=self.test_base,
        )
        self.analyzer.analyze()

    def get_suggestions(self):
        pass
