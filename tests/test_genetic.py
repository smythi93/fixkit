import ast
import os
import random
import unittest
from pathlib import Path

from pyrep.candidate import Candidate
from pyrep.genetic.crossover import OnePointCrossover
from pyrep.genetic.operators import (
    Delete,
    InsertBefore,
    Replace,
    MoveBefore,
    Swap,
    Copy,
    InsertAfter,
    MoveAfter,
)
from pyrep.stmt import StatementFinder


class TestGenetic(unittest.TestCase):
    file = None
    finder = None
    candidate = None
    statements = None

    @classmethod
    def setUpClass(cls):
        cls.file = Path("test.py")
        with cls.file.open("w") as fp:
            fp.write("x = 1\ny = 2")
        cls.finder = StatementFinder(cls.file)
        cls.finder.search_source()
        cls.candidate = cls.finder.build_candidate()
        cls.statements = cls.finder.statements
        cls.statements[3] = ast.Assign(targets=[ast.Name(id="z")], value=ast.Num(n=3))
        cls.tree = cls.candidate.TREES["."]

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file)


class TestMutations(TestGenetic):
    def verify_assign(self, node: ast.AST, var: str, val: int):
        self.assertIsInstance(node, ast.Assign)
        self.assertEqual(1, len(node.targets))
        self.assertIsInstance(node.targets[0], ast.Name)
        name: ast.Name = node.targets[0]
        self.assertEqual(var, name.id)
        self.assertIsInstance(node.value, ast.Constant)
        self.assertEqual(val, node.value.value)

    def test_delete(self):
        mutation = Delete(0, self.candidate.src, [3])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Pass)
        self.verify_assign(tree.body[1], "y", 2)

    def test_insert_before(self):
        mutation = InsertBefore(0, self.candidate.src, [3])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "z", 3)
        self.verify_assign(module.body[1], "x", 1)
        self.verify_assign(tree.body[1], "y", 2)

    def test_insert_after(self):
        mutation = InsertAfter(0, self.candidate.src, [3])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "x", 1)
        self.verify_assign(module.body[1], "z", 3)
        self.verify_assign(tree.body[1], "y", 2)

    def test_replace(self):
        mutation = Replace(0, self.candidate.src, [3])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.verify_assign(tree.body[0], "z", 3)
        self.verify_assign(tree.body[1], "y", 2)

    def test_move_before(self):
        mutation = MoveBefore(1, self.candidate.src, [0])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "y", 2)
        self.verify_assign(module.body[1], "x", 1)
        self.assertIsInstance(tree.body[1], ast.Pass)

    def test_move_after(self):
        mutation = MoveAfter(0, self.candidate.src, [1])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Pass)
        self.assertIsInstance(tree.body[1], ast.Module)
        module: ast.Module = tree.body[1]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "y", 2)
        self.verify_assign(module.body[1], "x", 1)

    def test_swap(self):
        mutation = Swap(0, self.candidate.src, [1])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.verify_assign(tree.body[0], "y", 2)
        self.verify_assign(tree.body[1], "x", 1)

    def test_copy(self):
        mutation = Copy(0, self.candidate.src, [])
        stmts = dict(self.statements)
        tree = mutation.mutate(self.tree, stmts)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "x", 1)
        self.verify_assign(module.body[1], "x", 1)
        self.verify_assign(tree.body[1], "y", 2)

    def test_multiple_mutations(self):
        m1 = Delete(0, self.candidate.src, [])
        m2 = Replace(0, self.candidate.src, [3])
        m3 = Copy(1, self.candidate.src, [])
        m4 = MoveBefore(0, self.candidate.src, [1])
        m5 = Delete(1, self.candidate.src, [])
        m6 = InsertAfter(1, self.candidate.src, [3])
        stmts = dict(self.statements)
        tree = m1.mutate(self.tree, stmts)
        tree = m2.mutate(tree, stmts)
        tree = m3.mutate(tree, stmts)
        tree = m4.mutate(tree, stmts)
        tree = m5.mutate(tree, stmts)
        tree = m6.mutate(tree, stmts)

        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Pass)
        self.assertIsInstance(tree.body[1], ast.Module)
        module_1: ast.Module = tree.body[1]
        self.assertEqual(2, len(module_1.body))
        self.assertIsInstance(module_1.body[0], ast.Module)
        module_2: ast.Module = module_1.body[0]
        self.assertEqual(2, len(module_2.body))
        self.verify_assign(module_2.body[0], "z", 3)
        self.assertIsInstance(module_2.body[1], ast.Module)
        module_3: ast.Module = module_2.body[1]
        self.assertEqual(2, len(module_3.body))
        self.assertIsInstance(module_3.body[0], ast.Pass)
        self.verify_assign(module_3.body[1], "z", 3)
        self.verify_assign(module_1.body[1], "y", 2)


class TestCrossover(TestGenetic):
    def _test_with_seed(self, seed: int):
        px = self.candidate.clone()
        py = self.candidate.clone()
        px.mutations = [
            Delete(0, self.candidate.src, []),
            InsertBefore(0, self.candidate.src, [3]),
        ]
        py.mutations = [
            MoveAfter(0, self.candidate.src, [1]),
            Replace(0, self.candidate.src, [1]),
        ]
        random.seed(seed)
        crossover = OnePointCrossover()
        cx, cy = crossover.crossover(px, py)
        self.assertIsInstance(cx, Candidate)
        self.assertIsInstance(cy, Candidate)
        return px, py, cx, cy

    def test_crossover_0(self):
        px, py, cx, cy = self._test_with_seed(0)
        self.assertEqual(2, len(cx))
        self.assertEqual(2, len(cy))
        self.assertEqual(px.mutations[:1] + py.mutations[1:], cx.mutations)
        self.assertEqual(py.mutations[:1] + px.mutations[1:], cy.mutations)

    def test_crossover_1(self):
        px, py, cx, cy = self._test_with_seed(1)
        self.assertEqual(0, len(cx))
        self.assertEqual(4, len(cy))
        self.assertEqual([], cx.mutations)
        self.assertEqual(py.mutations + px.mutations, cy.mutations)
