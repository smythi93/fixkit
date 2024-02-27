import unittest

from pyrep.fitness import GenProgFitness
from utils import LOCALIZATION


class TestFitness(unittest.TestCase):
    def test_gen_prog_fittness(self):
        fitness = GenProgFitness(
            {
                "tests.py::MiddleTestCase::test_middle_123",
                "tests.py::MiddleTestCase::test_middle_321",
                "tests.py::MiddleTestCase::test_middle_335",
                "tests.py::MiddleTestCase::test_middle_534",
                "tests.py::MiddleTestCase::test_middle_555",
            },
            {"tests.py::MiddleTestCase::test_middle_213"},
            1,
            10,
        )
        self.assertAlmostEqual(5, fitness.fitness(LOCALIZATION), delta=0.000001)
