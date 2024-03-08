import os
import unittest

from pyrep.fitness.metric import GenProgFitness
from utils import SUBJECTS


class TestFitness(unittest.TestCase):
    def tearDown(self):
        try:
            os.remove(SUBJECTS / "middle" / ".report.json")
        except OSError:
            pass

    def test_gen_prog_fittness(self):
        fitness = GenProgFitness(
            {
                "t4p.py::MiddleTestCase::test_middle_123",
                "t4p.py::MiddleTestCase::test_middle_321",
                "t4p.py::MiddleTestCase::test_middle_335",
                "t4p.py::MiddleTestCase::test_middle_534",
                "t4p.py::MiddleTestCase::test_middle_555",
            },
            {"t4p.py::MiddleTestCase::test_middle_213"},
            1,
            10,
        )
        self.assertAlmostEqual(
            1 / 3, fitness.evaluate_fitness(SUBJECTS / "middle"), delta=0.000001
        )
