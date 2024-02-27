import shutil
import unittest

from pyrep.candidate import GeneticCandidate
from pyrep.fitness.engine import Engine
from pyrep.fitness.metric import GenProgFitness
from utils import SUBJECTS, REP


class TestEngine(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)

    def run_test(self, workers: int):
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
        candidates = list()
        for i in range(2 * workers):
            candidates.append(GeneticCandidate(SUBJECTS / "middle"))
        for candidate in candidates:
            self.assertAlmostEqual(0, candidate.fitness, delta=0.000001)
        engine = Engine(fitness, workers)
        engine.evaluate(candidates)
        for candidate in candidates:
            self.assertAlmostEqual(5, candidate.fitness, delta=0.000001)

    def test_engine_1(self):
        self.run_test(1)

    def test_engine_5(self):
        self.run_test(5)
