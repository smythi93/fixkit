import random
import shutil
import unittest
import ast
from pathlib import Path
from utils import SUBJECTS, REP, SFL
import os

from pyrep.constants import DEFAULT_WORK_DIR, DEFAULT_EXCLUDES
from pyrep.genetic.operators import Replace
from pyrep.genetic.templates import Template, TemplateInstance, Scope_Constructor, Scope
from pyrep.localization.coverage import CoverageLocalization
from pyrep.localization.t4p import Tests4PyLocalization
from pyrep.repair.patch import write_patches
from pyrep.repair.pygenprog import PyGenProg, SingleMutationPyGenProg
from pyrep.repair.pykali import PyKali
from pyrep.repair.pymutrepair import PyMutRepair
from pyrep.repair.pycardumen import PyCardumen
from pyrep.logger import debug_logger
from pyrep.localization.normalization import normalize



class TestCardumen(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(SFL, ignore_errors=True)

    def setUp(self):
        self.cardumen = PyCardumen.from_source(
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
        self.cardumen : PyCardumen

        if(type(self.cardumen.initial_candidate.statements[15]).__name__ == "Assign"):
            self.assign_stmt = self.cardumen.initial_candidate.statements[16]

        if(type(self.cardumen.initial_candidate.statements[9]).__name__ == "Return"):
            self.return_stmt = self.cardumen.initial_candidate.statements[9]

        collector = Scope_Constructor()
        for tree in self.cardumen.initial_candidate.trees.values():
            collector.search(tree)
        
        self.stmt_scope = collector.scope_stmt

    def test_cardumen_filter_template_pool(self):
        #testing local vs global vs folder
        file = "middle.py"
        tmpls_local = self.cardumen.filter_template_pool("local", file, self.assign_stmt)
        tmpls_global = self.cardumen.filter_template_pool("global", file, self.assign_stmt)
        tmpls_folder = self.cardumen.filter_template_pool("folder", file, self.assign_stmt)
        self.assertTrue(len(tmpls_global) >= len(tmpls_folder) >= len(tmpls_local))
        #testing code type
        file = "global_path/global.py"
        tmpls_same_type = self.cardumen.filter_template_pool("local", file, self.return_stmt, code_type_mode=True)
        self.assertTrue(tmpl.target_code_type == "Return" for tmpl in tmpls_same_type)

    def test_cardumen_selecting_template(self):
        stmt = self.return_stmt
        tmpl = self.cardumen.selecting_template(self.cardumen.template_pool, stmt)
        #Schwierig eine Assertion zu machen, da Randomness
        #Das stmt und die tmpl sollten in etwa die gleichen Var Namen haben aber halt auch nicht immer
        self.assertTrue(isinstance(tmpl, Template))

    def test_cardumen_instance_template(self):
        stmt = self.assign_stmt       
        tmpl = self.cardumen.selecting_template(self.cardumen.template_pool, stmt)
        tmpl_instances = self.cardumen.instance_template(tmpl, stmt, self.stmt_scope)
        for tmpl_instance in tmpl_instances:
            self.assertTrue(isinstance(tmpl_instance, TemplateInstance))
        #good assertion needed len over instances??

    def test_cardumen_selecting_template_instance(self):
        statements = self.cardumen.initial_candidate.statements
        stmt = self.cardumen.initial_candidate.statements[3]
        tmpl = self.cardumen.selecting_template(self.cardumen.template_pool, stmt)
        tmpl_instances = self.cardumen.instance_template(tmpl, stmt, self.stmt_scope)
        tmpl_instance = self.cardumen.selecting_template_instance(statements, tmpl_instances)
        self.assertTrue(isinstance(tmpl_instance, TemplateInstance))
    
    def test_repair_middle_pycardumen(self):
        random.seed(6)
        patches = self.cardumen.repair()
        
        self.assertGreater(len(patches), 0)
        #self.assertAlmostEqual(1, patches[0].fitness, delta=0.000001)
        write_patches(patches, out=REP)
        self.assertTrue((REP / "patches" / "1.patch").exists())
    

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("tmp", ignore_errors=True)
    

if __name__ == "__main__":
    unittest.main()