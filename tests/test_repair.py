import random
import shutil
import unittest
from pathlib import Path

from pyrep.constants import DEFAULT_WORK_DIR
from pyrep.localization.coverage import CoverageLocalization
from pyrep.repair.patch import write_patches
from pyrep.repair.pygenprog import SingleMutationPyGenProg
from utils import SUBJECTS, REP


class TestRepair(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)

    def test_repair_middle(self):
        repair = SingleMutationPyGenProg.from_source(
            src=SUBJECTS / "middle",
            excludes=["tests.py"],
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
