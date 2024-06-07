import random
import shutil
import unittest
from pathlib import Path
from utils import SUBJECTS, REP, SFL

import tests4py.api as t4p

from fixkit.constants import DEFAULT_EXCLUDES
from fixkit.genetic.operators import Replace
from fixkit.localization.coverage import CoverageLocalization
from fixkit.localization.t4p import Tests4PyLocalization
from fixkit.repair.patch import write_patches
from fixkit.repair.pygenprog import PyGenProg, SingleMutationPyGenProg
from fixkit.repair.pykali import PyKali
from fixkit.logger import debug_logger
from fixkit.repair.pymutrepair import PyMutRepair
from utils import SUBJECTS, REP, SFL


class TestRepair(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(SFL, ignore_errors=True)

    def test_repair_middle_pygen(self):
        repair = PyGenProg.from_source(
            src=SUBJECTS / "middle",
            excludes=["tests.py"],
            localization=CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
                out=REP,
            ),
            population_size=40,
            max_generations=10,
            w_mut=0.06,
            workers=16,
            out=REP,
        )
        random.seed(6)
        patches = repair.repair()
        self.assertGreater(len(patches), 0)
        self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        write_patches(patches, out=REP)
        self.assertTrue((REP / "patches" / "1.patch").exists())

    @unittest.skip
    def test_repair_middle_pykali(self):
        repair = PyKali.from_source(
            src=SUBJECTS / "middle",
            excludes=["tests.py"],
            localization=CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
                out=REP,
            ),
            max_generations=3,
            w_mut=0.06,
            workers=16,
            out=REP,
        )
        
        random.seed(6)
        patches = repair.repair()
        #self.assertEqual(1, len(patches))
        #self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        #write_patches(patches, out=REP)
        #self.assertTrue((REP / "patches" / "1.patch").exists())

    @unittest.skip
    def test_repair_middle_pymutrepair(self):
        repair = PyMutRepair.from_source(
            src=SUBJECTS / "middle",
            excludes=["tests.py"],
            localization=CoverageLocalization(
                SUBJECTS / "middle",
                cov="middle",
                metric="Ochiai",
                tests=["tests.py"],
                out=REP,
            ),
            population_size=40,
            max_generations=3,
            w_mut=0.06,
            workers=16,
            out=REP,
        )
        
        random.seed(6)
        patches = repair.repair()
        #self.assertEqual(1, len(patches))
        #self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        #write_patches(patches, out=REP)
        #self.assertTrue((REP / "patches" / "1.patch").exists())
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("tmp", ignore_errors=True)
    
    @unittest.skip
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
            out=REP,
        )
        repair.operator = [Replace]
        repair.operator_weights = [1]
        random.seed(0)
        patches = repair.repair()
        self.assertEqual(1, len(patches))
        self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        write_patches(patches, out=REP)
        self.assertTrue((REP / "patches" / "1.patch").exists())

if __name__ == "__main__":
    unittest.main()