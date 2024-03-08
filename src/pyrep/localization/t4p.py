"""
The t4p module provides the necessary tools to localize a fault using Tests4Py.
"""

from tests4py import sfl

from pyrep.localization.sflkit import SFLKitLocalization


class Tests4PyLocalization(SFLKitLocalization):
    """
    Class for localizing a fault using Tests4Py.
    """

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
