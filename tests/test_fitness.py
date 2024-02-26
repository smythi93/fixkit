import unittest

from pyrep.fitness import GenProgFitness
from pyrep.localization.coverage import CoverageLocalization
from utils import SUBJECTS


class TestFitness(unittest.TestCase):
    def test_gen_prog_fittness(self):
        localization = CoverageLocalization(
            SUBJECTS / "middle",
            cov="middle",
            metric="Ochiai",
            tests=["tests.py"],
        )
        localization.prepare()
        fitness = GenProgFitness(localization.passing, localization.failing, 1, 10)
        self.assertAlmostEqual(5, fitness.fitness(SUBJECTS / "middle"), delta=0.000001)
