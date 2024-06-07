"""
The t4p module provides the necessary tools to localize a fault using Tests4Py.
"""
import os
from typing import Optional, List, Dict

from tests4py import sfl

from fixkit.localization.sflkit import SFLKitLocalization


class Tests4PyLocalization(SFLKitLocalization):
    """
    Class for localizing a fault using Tests4Py.
    """

    def _run_tests(self) -> sfl.SFLEventsReport:
        """
        Run the tests leveraging Tests4Py's sfl interface.
        :return: The report of the tests.
        """
        return sfl.sflkit_unittest(self.config.instrument_working)

    def run_preparation(self):
        """
        Run the preparation for the localization leveraging Tests4Py's sfl interface.
        """
        # Instrument the source code.
        report = sfl.sflkit_instrument(
            self.config.instrument_working,
            self.config.target_path,
            events=",".join(self.events) if self.events else "line",
        )
        if report.raised:
            raise report.raised
        # Run the tests and record the events.
        report = sfl.sflkit_unittest(self.config.instrument_working)
        if report.raised:
            raise report.raised

        self.passing = set(report.passing)
        self.failing = set(report.failing)
        # Analyze the events.
        report = sfl.sflkit_analyze(
            self.config.instrument_working,
            self.config.target_path,
            metrics=self.metric.__name__,
            predicates=",".join(self.predicates) if self.predicates else "",
        )
        if report.raised:
            raise report.raised
        self.analyzer = report.analyzer


class Tests4PySystemtestsLocalization(Tests4PyLocalization):
    def __init__(
        self,
        src: os.PathLike,
        tests: os.PathLike | list[os.PathLike],
        failing: Optional[List[str]] = None,
        passing: Optional[List[str]] = None,
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
        super().__init__(
            src,
            failing=failing,
            passing=passing,
            tests=tests,
            out=out,
            env=env,
            events=events,
            predicates=predicates,
            metric=metric,
            events_path=events_path,
            included_files=included_files,
            excluded_files=excluded_files,
            test_base=test_base,
        )

    def _run_tests(self) -> sfl.SFLEventsReport:
        """
        Run the tests leveraging Tests4Py's sfl interface.
        :return: The report of the tests.
        """
        return sfl.sflkit_systemtests(self.config.instrument_working, self.tests)
