import os
import unittest
from typing import Generator

from fixkit.candidate import GeneticCandidate
from fixkit.genetic.operators import MutationOperator, Delete, InsertBefore
from fixkit.localization.coverage import CoverageLocalization
from fixkit.repair.pyae import AbstractAE, PyAE
from fixkit.repair.repair import GeneticRepair
from tests.utils import SUBJECTS, REP


class AETest(unittest.TestCase):
    def test_edits(self):
        class TestAE(AbstractAE):
            @classmethod
            def _from_source(cls, src: os.PathLike, *args, **kwargs) -> GeneticRepair:
                pass

            def test_strategy(self, model):
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

    def test_repair(self):
        ae = PyAE.from_source(
            src=SUBJECTS / "middle",
            excludes=["tests.py"],
            localization=CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
                out=REP,
            ),
            out=REP,
            k=1,
        )
        patches = ae.repair()
        self.assertEqual(1, len(patches))
        patch = patches[0]
        self.assertEqual(1, len(patch.mutations))
        mutation = patch.mutations[0]
        self.assertIsInstance(mutation, InsertBefore)
        self.assertEqual(5, mutation.identifier)
        self.assertEqual(9, mutation.selection_identifier)
