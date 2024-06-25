import random
import shutil
import unittest

from fixkit.genetic.templates import Template, TemplateInstance, Scope_Constructor
from fixkit.localization.coverage import CoverageLocalization
from fixkit.repair.patch import write_patches
from fixkit.repair.pycardumen import PyCardumen
from utils import SUBJECTS, REP, SFL


class TestCardumen(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(SFL, ignore_errors=True)

    def setUp(self):
        self.cardumen: PyCardumen = PyCardumen.from_source(
            src=SUBJECTS / "middle_cardumen",
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

        if type(self.cardumen.initial_candidate.statements[17]).__name__ == "Assign":
            self.assign_stmt = self.cardumen.initial_candidate.statements[17]

        if type(self.cardumen.initial_candidate.statements[9]).__name__ == "Return":
            self.return_stmt = self.cardumen.initial_candidate.statements[9]

        collector = Scope_Constructor()
        for tree in self.cardumen.initial_candidate.trees.values():
            collector.search(tree)

        self.stmt_scope = collector.scope_stmt

    def test_cardumen_filter_template_pool(self):
        # testing local vs global vs folder
        file = "middle.py"
        templates_local = self.cardumen.filter_template_pool(
            "local", file, self.assign_stmt
        )
        templates_global = self.cardumen.filter_template_pool(
            "global", file, self.assign_stmt
        )
        templates_folder = self.cardumen.filter_template_pool(
            "folder", file, self.assign_stmt
        )
        self.assertTrue(
            len(templates_global) >= len(templates_folder) >= len(templates_local)
        )
        # testing code type
        file = "global_path/global.py"
        templates_same_type = self.cardumen.filter_template_pool(
            "local", file, self.return_stmt, code_type_mode=True
        )
        self.assertTrue(
            tmpl.target_code_type == "Return" for tmpl in templates_same_type
        )

    def test_cardumen_selecting_template(self):
        stmt = self.return_stmt
        template = self.cardumen.selecting_template(self.cardumen.template_pool, stmt)
        self.assertTrue(isinstance(template, Template))

    def test_cardumen_instance_template(self):
        stmt = self.assign_stmt
        template = self.cardumen.selecting_template(self.cardumen.template_pool, stmt)
        template_instances = self.cardumen.instance_template(
            template, stmt, self.stmt_scope
        )
        for tmpl_instance in template_instances:
            self.assertTrue(isinstance(tmpl_instance, TemplateInstance))
        # good assertion needed len over instances??

    def test_cardumen_selecting_template_instance(self):
        stmt = self.cardumen.initial_candidate.statements[3]
        tmpl = self.cardumen.selecting_template(self.cardumen.template_pool, stmt)
        tmpl_instances = self.cardumen.instance_template(tmpl, stmt, self.stmt_scope)
        tmpl_instance = self.cardumen.selecting_template_instance(tmpl_instances)
        self.assertTrue(isinstance(tmpl_instance, TemplateInstance))

    def test_repair_middle_pycardumen(self):
        random.seed(6)
        patches = self.cardumen.repair()

        self.assertGreater(len(patches), 0)
        write_patches(patches, out=REP)
        self.assertTrue((REP / "patches" / "1.patch").exists())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("tmp", ignore_errors=True)
