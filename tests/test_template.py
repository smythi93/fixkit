import unittest
import ast

from pyrep.genetic.templates import Template, ProbabilisticModel

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
        #code_1 = """z = 4 + 9"""
        #tree_1 = ast.parse(code_1)
        #code_2 = """x = y + 1"""
        #tree_2 = ast.parse(code_2)
        code_3 = """a = b + c"""
        tree_3 = ast.parse(code_3)
        self.statements = {
            #1 : tree_1,
            #2 : tree_2,
            3 : tree_3,
        }

    @unittest.skip
    def test_creating_template(self):
        tree = ast.parse(self.code)
        tmpl = Template(tree)
        new_vars = ["var_" + str(x) for x in range(0,len(tmpl.nodes))]
        new_tree = tmpl.apply_Changes(new_vars)
        print("Old:")
        print(ast.unparse(tree))
        print("New:")
        print(ast.unparse(new_tree))
    
    def test_probabilistic_model(self):
        model = ProbabilisticModel(self.statements)



if __name__ == "__main__":
    unittest.main()