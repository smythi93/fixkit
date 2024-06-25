import unittest
import ast

from fixkit.genetic.templates import Template, ProbabilisticModel


class TestTemplate(unittest.TestCase):
    def setUp(self) -> None:
        self.code = """
a = 1
b = 2
def foo():
    c = 3
    return c
class Bar:
    d = 4
    def method(self):
        e = 5
        f = e + d
"""
        self.code_1 = """c = d + 5"""
        tree_1 = ast.parse(self.code_1)
        code_2 = """b = c + 1"""
        tree_2 = ast.parse(code_2)
        code_3 = """a = b + c"""
        tree_3 = ast.parse(code_3)
        self.statements = {
            1: tree_1,
            2: tree_2,
            3: tree_3,
        }

    def test_creating_template(self):
        tree = ast.parse(self.code_1)
        tmpl = Template(tree, "path")

        tmpl_instances, _ = tmpl.construct_all_Combinations(["1", "2", "3", "4"])
        for instance in tmpl_instances:
            print(ast.unparse(instance))

    @unittest.skip
    def test_probabilistic_model(self):
        model = ProbabilisticModel(self.statements)
        print(model.probabilities)


if __name__ == "__main__":
    unittest.main()
