import ast
import random

from copy import deepcopy
from typing import List


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
        for var_name, nodes in self.nodes.items():
            var = random.choice(new_vars)
            new_vars.remove(var)
            for node in nodes:
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
        self.nodes = {}

    def visit_arg(self, node: ast.arg):
        if not node.arg == "self":
            if node.arg not in self.nodes:
                self.nodes[node.arg] = []
            self.nodes[node.arg].append(node)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if node.id not in self.nodes:
            self.nodes[node.id] = []
        self.nodes[node.id].append(node)
        self.generic_visit(node)

class ProbalisticModel:
    pass

