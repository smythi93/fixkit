import json
import os
import re
import shutil
import subprocess
from typing import Optional, List, Dict

from sflkit.analysis.spectra import Spectrum

from pyrep.localization import Localization, WeightedLocation

CONTEXT_PATTERN = re.compile(r"(?P<test>[^|]+)\|run")


class CoverageLocalization(Localization):
    def __init__(
        self,
        src: os.PathLike,
        cov: str,
        failing: Optional[List[str]] = None,
        passing: Optional[List[str]] = None,
        tests: Optional[List[str]] = None,
        out: Optional[os.PathLike] = None,
        env: Optional[Dict[str, str]] = None,
        metric: Optional[str] = None,
    ):
        super().__init__(src, failing, passing, tests, out, env, metric)
        self.cov = cov
        self.spectra = list()

    def run_preparation(self):
        shutil.copytree(self.src, self.out, dirs_exist_ok=True)
        passing_failing = (self.passing or list()) + (self.failing or list())
        tests = passing_failing or self.tests or ["tests"]
        subprocess.run(
            [
                "python",
                "-m",
                "pytest",
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
        passing = set()
        failing = set()
        with open(self.out / ".report.json") as fp:
            results = json.load(fp)
        for result in results["tests"]:
            if result["outcome"] == "passed":
                passing.add(result["nodeid"])
            else:
                failing.add(result["nodeid"])
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
                        if test in passing:
                            po += 1
                        elif test in failing:
                            fo += 1
                pn, fn = len(passing) - po, len(failing) - fo
                self.spectra.append(Spectrum(file, line, po, pn, fo, fn))

    def get_suggestions(self):
        return [WeightedLocation(s.file, s.line, self.metric(s)) for s in self.spectra]
