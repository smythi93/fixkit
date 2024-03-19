import random
import shutil
import unittest
from pathlib import Path

import tests4py.api as t4p

from pyrep.constants import DEFAULT_WORK_DIR, DEFAULT_EXCLUDES
from pyrep.genetic.operators import Replace
from pyrep.localization.coverage import CoverageLocalization
from pyrep.localization.t4p import Tests4PyLocalization
from pyrep.repair.patch import write_patches
from pyrep.repair.pygenprog import PyGenProg, SingleMutationPyGenProg
from utils import SUBJECTS, REP, SFL


class TestRepair(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(SFL, ignore_errors=True)

    def test_repair_middle(self):
        repair = PyGenProg.from_source(
            src=SUBJECTS / "middle",
            excludes=["t4p.py"],
            localization=CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
            ),
            population_size=40,
            max_generations=10,
            w_mut=0.06,
            workers=16,
        )
        random.seed(6)
        patches = repair.repair()
        self.assertEqual(1, len(patches))
        self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        write_patches(patches)
        self.assertTrue(Path(DEFAULT_WORK_DIR / "patches" / "1.patch").exists())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("tmp", ignore_errors=True)

    def test_repair_t4p(self):
        report = t4p.checkout(t4p.middle_2, Path("tmp"))
        if report.raised:
            raise report.raised
        repair = SingleMutationPyGenProg.from_source(
            Path("tmp", "middle_2"),
            excludes=DEFAULT_EXCLUDES,
            localization=Tests4PyLocalization(
                Path("tmp", "middle_2"),
                events=["line"],
                predicates=["line"],
                metric="Ochiai",
            ),
            population_size=10,
            max_generations=1,
            w_mut=0.06,
            workers=10,
            is_t4p=True,
            line_mode=True,
        )
        repair.operator = [Replace]
        repair.operator_weights = [1]
        random.seed(0)
        patches = repair.repair()
        self.assertEqual(1, len(patches))
        self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        write_patches(patches)
        self.assertTrue(Path(DEFAULT_WORK_DIR / "patches" / "1.patch").exists())
