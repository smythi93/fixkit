import unittest

from pyrep.candidate import GeneticCandidate
from pyrep.genetic.operators import Replace
from pyrep.patch import get_patches
from pyrep.stmt import StatementFinder
from utils import SUBJECTS


class TestDiff(unittest.TestCase):
    def test_diff(self):
        finder = StatementFinder(SUBJECTS / "middle", excludes=["tests.py"])
        finder.search_source()
        candidate = GeneticCandidate.from_candidate(finder.build_candidate())
        candidate.mutations = [Replace(5, [9])]
        patches = get_patches([candidate])
        pass
