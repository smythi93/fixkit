import unittest
from fixkit.genetic.operators import Delete, Copy, Rename, Variable_Collector
from fixkit.genetic.operators import InsertReturn0, InsertReturnList, InsertReturnString, InsertReturnNone
from fixkit.genetic.operators import InsertAfter, InsertBefore, InsertBoth, Replace
import ast
from fixkit.stmt import StatementFinder
from utils import SUBJECTS, REP
from fixkit.candidate import GeneticCandidate

class TestInsertReturn(ast.NodeVisitor):
    def __init__(self) -> None:
        self.found = False
        super().__init__()

    def visit_Return(self, node: ast.Return):
        if isinstance(node.value, ast.Constant) or isinstance(node.value, ast.List) or isinstance(node.value, ast.Tuple):
            self.found = True
        self.generic_visit(node)
    

class TestOperators(unittest.TestCase):
    def setUp(self):
        source_code = """z = 4 + 9"""
        tree = ast.parse(source_code)
        self.statements = {
            0 : ast.Add(),
            1 : ast.BinOp(ast.Constant(4), ast.Add(), ast.Constant(9)),
            2 : tree
        }

        self.mutations = {
            0 : ast.Pass(),
            1 : None,
            2 : ast.Pass()
        }

        finder = StatementFinder(SUBJECTS / "middle", excludes=["tests.py"])
        finder.search_source()
        self.candidate = GeneticCandidate.from_candidate(finder.build_candidate())
    
    def test_copy_operator(self):
        mutator = Copy(0)
        mutator.mutate(mutations=self.mutations, statements=self.statements)
        self.assertIsInstance(self.mutations[0], ast.Module)

    def test_delete_operator(self):
        mutator = Delete(1)
        mutator.mutate(mutations=self.mutations, statements=self.statements)
        self.assertIsInstance(self.mutations[1], ast.Pass)

    @unittest.skip
    #Es gibt ein Problem da wir statment für statment übergeben -> nur globalen scope -> visti_def, visit_class wird nicht getriggert -> die var werden nicht in self.names überschrieben :D
    #Zweites Problem, wenn das Statment mehr als ein ast.Name enthält ...
    def test_rename_operator(self):
        mutator = Rename(2)
        mutator.mutate(mutations=self.mutations, statements=self.statements)
        print(self.mutations[2])

        
    def test_variable_collector(self):
        collector = Variable_Collector(self.candidate.statements[2])
        collector.visit(self.candidate.trees["middle.py"])
        var_names = ["x", "y", "z"]
        for name in var_names:
            self.assertTrue(name in collector.names)
    
    def test_insert_return(self):
        id = 0
        mutators = [InsertReturn0(id), InsertReturnList(id), InsertReturnNone(id), InsertReturnString(id)]
        for mut in mutators:
            mut.mutate(mutations=self.mutations, statements=self.statements)
            test = TestInsertReturn()
            test.visit(self.mutations[id])
            self.assertTrue(test.found)

