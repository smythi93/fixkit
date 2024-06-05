import ast
import random

from copy import deepcopy
from typing import List, Dict, Tuple
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
        self.statement = statement
        collector = VarNodeCollector()
        collector.visit(self.statement)
        self.nodes = collector.nodes
        #original_vars used for selecting a Template from the Template Pool
        #könnte auch ein set sein?
        self.original_vars = []
        for node in self.nodes:
            if isinstance(node, ast.Name):
                self.original_vars.append(node.id)
            if isinstance(node, ast.arg):
                self.original_vars.append(node.arg)
        #TODO: Vorbereitung falls wir das wirklich benutzen
        self.return_type = "return_type"
        #TODO: keine ahnung was das sein soll -> Type from ast.Node exampe if , return
        self.target_code_type = "target_code_type"
        #TODO: Für filtering by location
        self.file = "file"
    
    def apply_Changes(self, new_vars: List) -> ast.AST:
        """
        Applys the new Variables to the Statement and returns the changed Statement
        """
        #TODO: I guess we have to do this copy stuff otherwise we cant reuse the Template or we have to run the VarNodeCollector everytime -> what is faster??
        #we also have to copy the nodes
        #i think its cleaner to run the collector all the time just for readability
        #oder kein copy stuff hier sondern sagen bevor applyChanges mach eine deepcopy von der template
        #oder ich merke die ursprünglichen einfach
        
        assert len(self.nodes) == len(new_vars)
        for node in self.nodes:
            var = random.choice(new_vars)
            new_vars.remove(var)
            if isinstance(node, ast.Name):
                node.id = var
            if isinstance(node, ast.arg):
                node.arg = var
        
        #Why do we do this:
        #In case we use the same template multiple times in one repair on different fault points -> sonst könnte sich
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


class ProbabilisticModel:
    """
    Creates a Probabilistic Model for usage of any given combinations of vars in the Program.
    p(vi .. vn) = number_of_statements_containing(vi .. vn) / all_statements_with_n_names
    """
    def __init__(self, statements: Dict[int, ast.AST]) -> None:
        self.statements = statements
        self.probabilities: Dict[Tuple[str, ...], float] = dict()
        self.createModel()

    def createModel(self) -> None:
        for statement in self.statements.values():
            collector = VarNamesCollector()
            collector.visit(statement)
            vars = collector.vars
            all_combinations = chain.from_iterable(combinations(vars, i) for i in range(1, len(vars) + 1))
            for combination in all_combinations:
                if combination not in self.probabilities.keys():
                    x, y = self.checkCombination(combination)
                    try:
                        probability = x / y
                    except ZeroDivisionError:
                        probability = 0.0
                    self.probabilities[combination] = probability

    #Was passiert wenn statement a = a +1
    #dann zweimal a wird nicht spezifiziert in paper
    #wird momentan ignoriert gehen davon aus das die element unique sind!!!
    def checkCombination(self, combination: List[str]) -> Tuple[int, int]:
        """
        Checks all the Statement if it contains the combination 
        or if the statment has the same number of vars as the combination
        """
        same_combination = 0
        same_number_of_vars = 0
        for statement in self.statements.values():
            visitor = VarNamesCollector()
            visitor.visit(statement)
            #Checks if the list contains the same elements -> elements need to be unique and hashable
            if set(combination) == set(visitor.vars):
                same_combination+=1
                same_number_of_vars+=1
                continue
            
            if len(visitor.vars) == len(combination):
                same_number_of_vars+=1
        
        return (same_combination, same_number_of_vars)
    

#TODO: Probabilistic Model with different Scopes taken into consideration