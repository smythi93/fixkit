import ast
import os
import random
import unittest
from pathlib import Path

from pyrep.candidate import GeneticCandidate
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
    Mutator,
    InsertBoth,
    MoveBoth,
)
from pyrep.stmt import StatementFinder


@unittest.skip("Skip until we have a better way to test this")
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
        cls.candidate = GeneticCandidate.from_candidate(cls.finder.build_candidate())
        cls.statements = cls.finder.statements
        cls.statements[2] = ast.Assign(
            targets=[ast.Name(id="z")], value=ast.Num(n=3), lineno=3
        )
        cls.tree = cls.candidate.trees["."]

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
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [Delete(0, [2])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Pass)
        self.verify_assign(tree.body[1], "y", 2)

    def test_insert_before(self):
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [InsertBefore(0, [2])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "z", 3)
        self.verify_assign(module.body[1], "x", 1)
        self.verify_assign(tree.body[1], "y", 2)

    def test_insert_after(self):
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [InsertAfter(0, [2])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "x", 1)
        self.verify_assign(module.body[1], "z", 3)
        self.verify_assign(tree.body[1], "y", 2)

    def test_replace(self):
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [Replace(0, [2])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.verify_assign(tree.body[0], "z", 3)
        self.verify_assign(tree.body[1], "y", 2)

    def test_move_before(self):
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [MoveBefore(1, [0])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Pass)
        self.assertIsInstance(tree.body[1], ast.Module)
        module: ast.Module = tree.body[1]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "x", 1)
        self.verify_assign(module.body[1], "y", 2)

    def test_move_after(self):
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [MoveAfter(0, [1])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "x", 1)
        self.verify_assign(module.body[1], "y", 2)
        self.assertIsInstance(tree.body[1], ast.Pass)

    def test_swap(self):
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [Swap(0, [1])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.verify_assign(tree.body[0], "y", 2)
        self.verify_assign(tree.body[1], "x", 1)

    def test_copy(self):
        stmts = dict(self.statements)
        mutator = Mutator(stmts, [Copy(0, [])])
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module: ast.Module = tree.body[0]
        self.assertEqual(2, len(module.body))
        self.verify_assign(module.body[0], "x", 1)
        self.verify_assign(module.body[1], "x", 1)
        self.verify_assign(tree.body[1], "y", 2)

    def test_multiple_mutations(self):
        stmts = dict(self.statements)
        mutator = Mutator(
            stmts,
            [
                Delete(0, []),
                Replace(0, [2]),
                Copy(1, []),
                MoveBefore(0, [1]),
                Delete(1, []),
                InsertAfter(1, [2]),
            ],
        )
        tree = mutator.mutate(self.tree)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(2, len(tree.body))
        self.assertIsInstance(tree.body[0], ast.Module)
        module_0: ast.Module = tree.body[0]
        self.assertEqual(2, len(module_0.body))
        self.assertIsInstance(module_0.body[0], ast.Module)
        module_0_0: ast.Module = module_0.body[0]
        self.assertEqual(2, len(module_0_0.body))
        self.verify_assign(module_0_0.body[0], "y", 2)
        self.verify_assign(module_0_0.body[1], "y", 2)
        self.verify_assign(module_0.body[1], "z", 3)
        self.assertIsInstance(tree.body[1], ast.Module)
        module_1: ast.Module = tree.body[1]
        self.assertEqual(2, len(module_1.body))
        self.assertIsInstance(module_1.body[0], ast.Pass)
        self.verify_assign(module_1.body[1], "z", 3)


class TestCrossover(TestGenetic):
    def _test_with_seed(self, seed: int):
        px = self.candidate.clone()
        py = self.candidate.clone()
        px.mutations = [
            Delete(0, []),
            InsertBefore(0, [2]),
        ]
        py.mutations = [
            MoveAfter(0, [1]),
            Replace(0, [1]),
        ]
        random.seed(seed)
        crossover = OnePointCrossover()
        cx, cy = crossover.crossover(px, py)
        self.assertIsInstance(cx, GeneticCandidate)
        self.assertIsInstance(cy, GeneticCandidate)
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


class TestEquality(unittest.TestCase):
    def test_equal(self):
        tests = [
            Delete(0, [0]),
            Delete(1, [0]),
            InsertAfter(0, [0]),
            InsertAfter(1, [0]),
            InsertBefore(0, [0]),
            InsertBefore(1, [0]),
            InsertBoth(0, [0]),
            InsertBoth(1, [0]),
            MoveAfter(0, [0]),
            MoveAfter(1, [0]),
            MoveBefore(0, [0]),
            MoveBefore(1, [0]),
            MoveBoth(0, [0]),
            MoveBoth(1, [0]),
            Replace(0, [0]),
            Replace(1, [0]),
            Copy(0, [0]),
            Copy(1, [0]),
        ]
        for i in range(len(tests)):
            for j in range(len(tests)):
                if i == j:
                    self.assertEqual(hash(tests[i]), hash(tests[j]))
                    self.assertEqual(tests[i], tests[j])
                else:
                    self.assertNotEqual(hash(tests[i]), hash(tests[j]))
                    self.assertNotEqual(tests[i], tests[j])
