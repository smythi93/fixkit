import unittest
import ast

from pyrep.genetic.templates import Template, VarNodeCollector

class TestTemplate(unittest.TestCase):
    def setUp(self) -> None:
        self.code = """
a = 1
b = 2
def foo(c, d):
    c = 3
    return c
class Bar:
    d = 4
"""
    
    def test_creating_template(self):
        tree = ast.parse(self.code)
        tmpl = Template(tree)
        new_vars = ["var_" + str(x) for x in range(1,8)]
        new_tree = tmpl.apply_Changes(new_vars)
        print("Old:")
        print(ast.unparse(tree))
        print("New:")
        print(ast.unparse(new_tree))
    
    

if __name__ == "__main__":
    unittest.main()