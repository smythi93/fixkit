import random
import unittest
from pathlib import Path

from pyrep.constants import DEFAULT_WORK_DIR
from pyrep.localization.coverage import CoverageLocalization
from pyrep.patch import get_patches
from pyrep.repair.pygenprog import SingleMutationPyGenProg
from utils import SUBJECTS


class TestRepair(unittest.TestCase):
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
            workers=4,
        )
        random.seed(5)
        patches = repair.repair()
        get_patches(patches)
        self.assertTrue(Path(DEFAULT_WORK_DIR / "patches" / "1.patch").exists())
