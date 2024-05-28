import ast
import unittest
from typing import List

from pyrep.embeddings.code2vec.granularity import (
    CorpusBuilder,
    GranularityBuilder,
    Granularity,
)
from utils import SUBJECTS


class TestCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = CorpusBuilder()

    def _test(self, test_case: str, expected: List[str]):
        self.assertEqual(expected, self.builder.visit(ast.parse(test_case)))

    def test_corpus_1(self):
        self._test("1", ["<INT>"])

    def test_corpus_2(self):
        self._test("y = x + 2", ["y", "x", "<INT>"])

    def test_corpus_3(self):
        self._test(
            """
def f(x: int, y: float):
    return x * y + 1.0

print("result: " + str(f(2, 3.0)))
""",
            [
                "f",
                "x",
                "int",
                "y",
                "float",
                "x",
                "y",
                "<FLOAT>",
                "print",
                "<STR>",
                "str",
                "f",
                "<INT>",
                "<FLOAT>",
            ],
        )


class TestGranularityBuilder(unittest.TestCase):
    def test_files(self):
        builder = GranularityBuilder(
            src=SUBJECTS / "granularity", granularity=Granularity.FILE
        )
        terminals = builder.build()
        self.assertEqual(2, len(terminals))
        self.assertIn(
            [
                "a",
                "<INT>",
                "b",
                "<INT>",
                "foo",
                "c",
                "<INT>",
                "c",
                "Bar",
                "d",
                "<INT>",
                "method",
                "self",
                "e",
                "<INT>",
                "f",
                "e",
                "self",
                "d",
            ],
            terminals,
        )
        self.assertIn(["Foo", "foobar", "<STR>", "staticmethod"], terminals)

    def test_classes(self):
        builder = GranularityBuilder(
            src=SUBJECTS / "granularity", granularity=Granularity.CLASS
        )
        terminals = builder.build()
        self.assertEqual(2, len(terminals))
        self.assertIn(
            ["Foo", "foobar", "<STR>", "staticmethod"],
            terminals,
        )
        self.assertIn(
            [
                "Bar",
                "d",
                "<INT>",
                "method",
                "self",
                "e",
                "<INT>",
                "f",
                "e",
                "self",
                "d",
            ],
            terminals,
        )

    def test_functions(self):
        builder = GranularityBuilder(
            src=SUBJECTS / "granularity", granularity=Granularity.FUNCTION
        )
        terminals = builder.build()
        self.assertEqual(3, len(terminals))
        self.assertIn(
            [
                "foo",
                "c",
                "<INT>",
                "c",
            ],
            terminals,
        )
        self.assertIn(
            [
                "method",
                "self",
                "e",
                "<INT>",
                "f",
                "e",
                "self",
                "d",
            ],
            terminals,
        )
        self.assertIn(
            ["foobar", "<STR>", "staticmethod"],
            terminals,
        )
