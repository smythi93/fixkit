import shutil
import unittest
from pathlib import Path

import tests4py.api as t4p

from pyrep.candidate import GeneticCandidate
from pyrep.fitness.engine import Engine, Tests4PyEngine
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
            self.assertAlmostEqual(1 / 3, candidate.fitness, delta=0.000001)

    def test_engine_1(self):
        self.run_test(1)

    def test_engine_5(self):
        self.run_test(5)


class TestTest4PyEngine(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        report = t4p.checkout(t4p.middle_2, Path("tmp"))
        if report.raised:
            raise report.raised

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("tmp")

    def run_test(self, workers: int):
        fitness = GenProgFitness(
            {
                "tests/test_middle.py::TestMiddle::test_middle_555",
                "tests/test_middle.py::TestMiddle::test_middle_123",
                "tests/test_middle.py::TestMiddle::test_middle_534",
                "tests/test_middle.py::TestMiddle::test_middle_321",
                "tests/test_middle.py::TestMiddle::test_middle_335",
            },
            {"tests/test_middle.py::TestMiddle::test_middle_213"},
        )
        candidates = list()
        for i in range(2 * workers):
            candidates.append(GeneticCandidate(Path("tmp", "middle_2")))
        for candidate in candidates:
            self.assertAlmostEqual(0, candidate.fitness, delta=0.000001)
        engine = Tests4PyEngine(fitness, workers)
        engine.evaluate(candidates)
        for candidate in candidates:
            self.assertAlmostEqual(1 / 3, candidate.fitness, delta=0.000001)

    def test_engine_1(self):
        self.run_test(1)

    def test_engine_5(self):
        self.run_test(5)
