import ast
import random

from copy import deepcopy
from typing import List, Dict
from itertools import combinations, chain

#Problems: Python not type based -> dadurch templates oft quatsch
#In Java werden double nur durch doubles ersetzt

#Vor Nutzung von applyChanges ScopeVariablen Collector benutzen -> Anzahl von Placeholdern in ProbalisticModel -> Und dann in applyChanges


class Template:
    """
    Creates a Template from the Statement.
    This Template can be inserted and changed with different Variables.
    Used for Cardumen approach.
    """
    def __init__(self, statement: ast.AST) -> None:
        """
        Inits the Template by collecting all Nodes of Variables.
        """
        self.statement = deepcopy(statement)
        collector = VarNodeCollector()
        collector.visit(self.statement)
        self.nodes = collector.nodes
    
    def apply_Changes(self, new_vars: List) -> ast.AST:
        """
        Applys the new Variables to the Statement and returns the changed Statement
        """
        assert(len(self.nodes) == len(new_vars))
        for node in self.nodes:
            var = random.choice(new_vars)
            new_vars.remove(var)
            if isinstance(node, ast.Name):
                node.id = var
            if isinstance(node, ast.arg):
                node.arg = var

        return self.statement

class VarNodeCollector(ast.NodeVisitor):
    """
    Collects all arg und name nodes of the statement it is visiting.

    collector = NameNodeCollector()
    collector.visit(stmt)
    nodes = collector.nodes
    """
    def __init__(self) -> None:
        self.nodes = []

    def visit_arg(self, node: ast.arg):
        if not node.arg == "self":
            self.nodes.append(node)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        self.nodes.append(node)
        self.generic_visit(node)

class VarNamesCollector(ast.NodeVisitor):
    """
    Collects all Variable Names of the statement it is visiting.

    collector = VarCollector()
    collector.visit(stmt)
    vars = collector.vars
    """
    def __init__(self) -> None:
        self.vars = []

    def visit_arg(self, node: ast.arg):
        if not node.arg == "self":
            self.vars.append(node.arg)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        self.vars.append(node.id)
        self.generic_visit(node)

class 
class ProbabilisticModel:
    """
    Creates a Probabilistic Model for usage of any given combinations of vars in the Program.
    p(vi .. vn) = number_of_statements_containing(vi .. vn) / all_statements_with_n_names
    """
    def __init__(self, statements: Dict[int, ast.AST]) -> None:
        self.statements = statements
        self.probabilities: Dict[:int] = dict()
        self.createModel()

    def createModel(self):
        for statement in self.statements.values():
            collector = VarNamesCollector()
            collector.visit(statement)
            vars = collector.vars
            all_combinations = [comb for i in range(1, len(vars) + 1) for comb in combinations(vars, i)]
            #all_combinations = list(chain.from_iterable(combinations(vars, i) for i in range(1, len(vars) + 1)))
            for combination in all_combinations:
                #combination = repr(combination)
                print(combination)
                if combination not in self.probabilities.keys():
                    pass







