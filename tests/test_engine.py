import os.path
import shutil
import unittest
from pathlib import Path

import tests4py.api as t4p

from fixkit.candidate import GeneticCandidate
from fixkit.fitness.engine import Engine, Tests4PyEngine, Tests4PySystemTestEngine
from fixkit.fitness.metric import GenProgFitness
from utils import SUBJECTS, REP, SFL


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
        engine = Engine(fitness, workers, out=REP)
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
        shutil.rmtree(SFL, ignore_errors=True)

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
        engine = Tests4PyEngine(fitness, workers, out=REP, raise_on_failure=True)
        engine.evaluate(candidates)
        for candidate in candidates:
            self.assertAlmostEqual(1 / 3, candidate.fitness, delta=0.000001)

    def run_system_test(self, workers: int):
        fitness = GenProgFitness(
            {
                os.path.join(SUBJECTS, "tests", "555"),
                os.path.join(SUBJECTS, "tests", "123"),
                os.path.join(SUBJECTS, "tests", "534"),
                os.path.join(SUBJECTS, "tests", "321"),
                os.path.join(SUBJECTS, "tests", "335"),
            },
            {os.path.join(SUBJECTS, "tests", "213")},
        )
        candidates = list()
        for i in range(2 * workers):
            candidates.append(GeneticCandidate(Path("tmp", "middle_2")))
        for candidate in candidates:
            self.assertAlmostEqual(0, candidate.fitness, delta=0.000001)
        engine = Tests4PySystemTestEngine(
            fitness,
            os.path.join(SUBJECTS, "tests"),
            workers,
            out=REP,
            raise_on_failure=True,
        )
        engine.evaluate(candidates)
        for candidate in candidates:
            self.assertAlmostEqual(1 / 3, candidate.fitness, delta=0.000001)

    def test_engine_1(self):
        self.run_test(1)

    def test_engine_5(self):
        self.run_test(5)

    def test_system_engine_1(self):
        self.run_system_test(1)

    def test_system_engine_5(self):
        self.run_system_test(5)
