import unittest
import ast

from pyrep.genetic.templates import Template, CreateTemplate

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
"""
    
    def test_creating_template(self):
        tree = ast.parse(self.code)
        transformer = CreateTemplate()
        transformed_tree = transformer.visit(tree)
        print(ast.dump(transformed_tree, indent=4))
    
    

if __name__ == "__main__":
    unittest.main()