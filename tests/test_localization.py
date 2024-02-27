import shutil
import unittest
from pathlib import Path

from pyrep.localization import Localization
from pyrep.localization.coverage import CoverageLocalization
from pyrep.localization.sflkit import SFLKitLocalization
from utils import SUBJECTS, REP, SFL


class TestLocalization(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(SFL, ignore_errors=True)

    def _base_test(self, localization: Localization):
        localization.prepare()
        suggestions = localization.get_sorted_suggestions()
        top_suggestion = suggestions[0]
        self.assertEqual("middle.py", top_suggestion.file)
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
            )
        )

    def test_coverage_localization(self):
        self._base_test(
            CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
            )
        )
