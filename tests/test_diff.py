import shutil
import unittest

from pyrep.candidate import GeneticCandidate
from pyrep.genetic.operators import Replace
from pyrep.repair.patch import get_patch
from pyrep.stmt import StatementFinder
from utils import SUBJECTS, REP


@unittest.skip("Skip until we have a better way to test this")
class TestDiff(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)

    def test_diff(self):
        finder = StatementFinder(SUBJECTS / "middle", excludes=["tests.py"])
        finder.search_source()
        candidate = GeneticCandidate.from_candidate(finder.build_candidate())
        candidate.mutations = [Replace(5, [9])]
        patch = get_patch(candidate, out=REP)
        self.assertEqual(
            "--- middle.py\n"
            "+++ middle.py\n"
            "@@ -3,10 +3,9 @@\n"
            "         if x < y:\n"
            "             return y\n"
            "         elif x < z:\n"
            "-            return y\n"
            "-    else:\n"
            "-        if x > y:\n"
            "-            return y\n"
            "-        elif x > z:\n"
            "             return x\n"
            "-    return z\n"
            "+    elif x > y:\n"
            "+        return y\n"
            "+    elif x > z:\n"
            "+        return x\n"
            "+    return z\n",
            patch,
        )
