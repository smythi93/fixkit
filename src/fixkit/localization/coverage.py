"""
The coverage module provides the necessary tools to localize a fault using coverage.py information.
"""
import time
import coverage
import json
import os
import re
import shutil
import subprocess
from typing import Optional, List, Dict

from sflkit.analysis.spectra import Spectrum

from fixkit.localization.localization import Localization
from fixkit.localization.location import WeightedLocation

from fixkit.logger import LOGGER

import signal
from pytest_cov.embed import cleanup_on_sigterm

# Regular expression for parsing the context of a coverage line.
CONTEXT_PATTERN = re.compile(r"(?P<test>[^|]+)\|run")


class CoverageLocalization(Localization):
    """
    Class for localizing a fault using coverage.py information.
    """

    def __init__(
        self,
        src: os.PathLike,
        cov: str,
        timeout: Optional[int] = 0,
        failing: Optional[List[str]] = None,
        passing: Optional[List[str]] = None,
        tests: Optional[List[str]] = None,
        out: Optional[os.PathLike] = None,
        env: Optional[Dict[str, str]] = None,
        metric: Optional[str] = None,
    ):
        """
        Initialize the coverage localization.
        :param os.PathLike src: The source directory of the project.
        :param str cov: The coverage.py data prefix.
        :param Optional[List[str]] failing: The set of failing tests, will override tests.
        :param Optional[List[str]] passing: The set of passing tests, will override tests.
        :param Optional[List[str]] tests: The set of all tests, as an alternative when an oracle exists.
        :param Optional[os.PathLike] out: The output directory for the localization.
        :param Optional[Dict[str, str]] env: The environment to run the tests in.
        :param Optional[str] metric: The metric to use for the localization.
        """
        super().__init__(src, timeout, failing, passing, tests, out, env, metric)
        self.cov = cov
        self.spectra = list()

    def run_preparation(self):
        """
        Run the preparation for the localization by executing the tests and collecting the coverage data.
        """
        shutil.copytree(self.src, self.out, dirs_exist_ok=True)
        # Get the passing and failing tests.
        passing_failing = (self.passing or set()) | (self.failing or set())
        tests = list(passing_failing or self.tests or {"tests"})
        # Run the tests and collect the coverage data.
        
        try:
            proc = subprocess.Popen(
                [
                    "python",
                    "-m",
                    "pytest",
                    f"--rootdir={self.out}",
                    "--cov",
                    self.cov,
                    "--cov-context",
                    "test",
                    "--json-report",
                ]
                + tests,
                cwd=self.out,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proc.wait(self.timeout)
        except subprocess.TimeoutExpired as e:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=5)
            cleanup_on_sigterm()
            LOGGER.info("testcases timeout expired.")
            LOGGER.info(e)
        # Parse the coverage data into a list of passing and failing spectra.
        self.passing = set()
        self.failing = set()
        with open(self.out / ".report.json") as fp:
            results = json.load(fp)
        for result in results["tests"]:
            if result["outcome"] == "passed":
                self.passing.add(result["nodeid"])
            else:
                self.failing.add(result["nodeid"])
        subprocess.run(
            ["coverage", "json", "-o", "tmp.json", "--show-context"],
            cwd=self.out,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with open(self.out / "tmp.json") as fp:
            coverage_data = json.load(fp)
        for file in coverage_data["files"]:
            for line in coverage_data["files"][file]["executed_lines"]:
                po, fo = 0, 0
                for test in coverage_data["files"][file]["contexts"][str(line)]:
                    match = CONTEXT_PATTERN.match(test)
                    if match:
                        test = match.group("test")
                        if test in self.passing:
                            po += 1
                        elif test in self.failing:
                            fo += 1
                pn, fn = len(self.passing) - po, len(self.failing) - fo
                self.spectra.append(Spectrum(file, line, po, pn, fo, fn))

    def get_suggestions(self) -> List[WeightedLocation]:
        """
        Get the suggestions of the localization by calculating the metric based on the spectra.
        :return List[WeightedLocation]: The list of weighted locations.
        """
        return [WeightedLocation(s.file, s.line, self.metric(s)) for s in self.spectra]


__all__ = ["CoverageLocalization"]
