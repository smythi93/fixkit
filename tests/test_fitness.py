import os
import shutil
import unittest

from pyrep.fitness.metric import GenProgFitness
from utils import SUBJECTS, REP


class TestFitness(unittest.TestCase):
    def tearDown(self):
        try:
            os.remove(SUBJECTS / "middle" / ".report.json")
        except OSError:
            pass
        shutil.rmtree(REP, ignore_errors=True)

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
        self.assertAlmostEqual(
            1 / 3, fitness.evaluate_fitness(SUBJECTS / "middle"), delta=0.000001
        )
