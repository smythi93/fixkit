import os.path
import shutil
import unittest
from pathlib import Path

import tests4py.api

from pyrep.localization import Localization
from pyrep.localization.coverage import CoverageLocalization
from pyrep.localization.sflkit import SFLKitLocalization
from pyrep.localization.t4p import Tests4PyLocalization
from utils import SUBJECTS, REP, SFL


class TestLocalization(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(SFL, ignore_errors=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("tmp", ignore_errors=True)

    def _base_test(self, localization: Localization, file: str = "middle.py"):
        localization.prepare()
        suggestions = localization.get_sorted_suggestions()
        top_suggestion = suggestions[0]
        self.assertEqual(file, top_suggestion.file)
        self.assertEqual(6, top_suggestion.line)
        self.assertAlmostEqual(
            0.7071067811865475, top_suggestion.weight, delta=0.000001
        )

    def test_sflkit_localization(self):
        self._base_test(
            SFLKitLocalization(
                SUBJECTS / "middle",
                events=["line"],
                predicates=["line"],
                metric="Ochiai",
                excluded_files=["tests.py"],
                tests=["tests.py"],
                out=REP,
            )
        )

    def test_coverage_localization(self):
        self._base_test(
            CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
                out=REP,
            )
        )

    def test_tests4py_localization(self):
        report = tests4py.api.checkout(tests4py.api.middle_2, Path("tmp"))
        if report.raised:
            raise report.raised
        self._base_test(
            Tests4PyLocalization(
                Path("tmp", "middle_2"),
                events=["line"],
                predicates=["line"],
                metric="Ochiai",
            ),
            file=os.path.join("src", "middle", "__init__.py"),
        )
