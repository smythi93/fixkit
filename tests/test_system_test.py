import os
import random
import shutil
import unittest
from pathlib import Path

import tests4py.api as t4p

from fixkit.constants import DEFAULT_EXCLUDES
from fixkit.genetic.operators import Replace
from fixkit.localization.t4p import Tests4PySystemtestsLocalization
from fixkit.repair import SingleMutationPyGenProg
from fixkit.repair.patch import write_patches
from utils import REP, SFL


class TestRepair(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(SFL, ignore_errors=True)
        shutil.rmtree("tmp", ignore_errors=True)

    def test_repair_middle(self):
        report = t4p.checkout(t4p.middle_2, Path("tmp"))
        if report.raised:
            raise report.raised
        test_cases = [
            os.path.abspath(
                os.path.join(
                    "tmp",
                    "middle_2",
                    "tests4py_systemtest_diversity",
                    "failing_test_diversity_0",
                )
            ),
            os.path.abspath(
                os.path.join(
                    "tmp",
                    "middle_2",
                    "tests4py_systemtest_diversity",
                    "passing_test_diversity_0",
                )
            ),
            os.path.abspath(
                os.path.join(
                    "tmp",
                    "middle_2",
                    "tests4py_systemtest_diversity",
                    "passing_test_diversity_1",
                )
            ),
        ]

        repair = SingleMutationPyGenProg.from_source(
            src=Path("tmp/middle_2/"),
            excludes=DEFAULT_EXCLUDES,
            localization=Tests4PySystemtestsLocalization(
                src=Path("tmp/middle_2/"),
                excluded_files=DEFAULT_EXCLUDES,
                tests=test_cases,
                metric="Ochiai",
                events=["line"],
                predicates=["line"],
            ),
            population_size=10,
            max_generations=1,
            w_mut=0.06,
            workers=10,
            out=REP,
            is_t4p=True,
            is_system_test=True,
            system_tests=test_cases,
            line_mode=True,
        )
        repair.operator = [Replace]
        repair.operator_weights = [1]
        random.seed(0)
        patches = repair.repair()
        self.assertEqual(1, len(patches))
        self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        write_patches(patches, out=REP)
        self.assertTrue((REP / "patches" / "1.patch").exists())
