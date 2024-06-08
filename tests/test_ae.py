import os
import unittest
from typing import Generator, List

from src.fixkit.candidate import GeneticCandidate
from src.fixkit.genetic.operators import MutationOperator, Delete
from src.fixkit.localization.coverage import CoverageLocalization
from src.fixkit.repair.pyae import AbstractAE
from src.fixkit.repair.repair import GeneticRepair
from tests.utils import SUBJECTS, REP


class AETest(unittest.TestCase):
    def test_edits(self):
        class TestAE(AbstractAE):
            @staticmethod
            def from_source(src: os.PathLike, *args, **kwargs) -> GeneticRepair:
                pass

            def test_strategy(self, candidate: List[GeneticCandidate], model):
                pass

            def equivalent(
                self, candidate_1: GeneticCandidate, candidate_2: GeneticCandidate
            ):
                return False

            def repair_strategy(self, model) -> Generator[MutationOperator, None, None]:
                for i in range(3):
                    yield Delete(identifier=i)

        ae = TestAE(
            GeneticCandidate(SUBJECTS / "middle"),
            localization=CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
                out=REP,
            ),
            population_size=40,
            max_generations=10,
            workers=16,
            out=REP,
            k=3,
        )

        expected = [[Delete(identifier=i)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                expected.append([Delete(identifier=i), Delete(identifier=j)])
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    expected.append(
                        [
                            Delete(identifier=i),
                            Delete(identifier=j),
                            Delete(identifier=k),
                        ]
                    )
        actual = list(ae.candidate_repairs(set()))
        for e in expected:
            self.assertIn(e, actual)
        for a in actual:
            self.assertIn(a, expected)
