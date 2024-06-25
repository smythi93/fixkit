import ast

from typing import List, Dict, Tuple, Iterable
from itertools import product, combinations_with_replacement
from copy import deepcopy
from multiset import FrozenMultiset

class Template():
    """
    Creates a Template from the Statement.
    This Template can be inserted and changed with different Variables.
    Used for Cardumen approach.
    """
    def __init__(self, statement: ast.AST, path: str):
        """
        Inits the Template by collecting all Nodes of Variables.
        """
        self.statement = statement
        self.path = path
        self.target_code_type = type(statement).__name__

        collector = VarNamesCollector()
        collector.visit(self.statement)
        self.vars = collector.vars
        self.count_placeholder = len(collector.vars)
        self.mapping = dict()
        for var in collector.vars:
            self.mapping[var] = var
    
    def __repr__(self) -> str:
        return f"Template: {ast.unparse(self.statement)}"

class TemplateTransformer(ast.NodeTransformer):
    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping

    def visit_Name(self, node: ast.Name):
        new_name = self.mapping[node.id]
        return ast.Name(id = new_name, ctx=node.ctx)
    
    def visit_arg(self, node: ast.arg):
        new_arg = self.mapping[node.arg]
        return ast.arg(arg=new_arg, annotation=node.annotation, type_comment=node.type_comment)

class Combination:
    def __init__(self, items: Iterable):
        self.items = FrozenMultiset(items)

class TemplateInstance():
    def __init__(self, template: Template, tree: ast.AST, combination: Combination, mapping: dict[str, str]):
        self.template = template
        self.tree = tree
        self.combination = combination
        self.mapping = mapping
        
    def __repr__(self) -> str:
        code = ast.unparse(self.tree)
        return f"TemplateInstance: {code}"

class TemplateInstanceGenerator():
    def __init__(self, template: Template):
        self.template = template

    def create_Mapping(self, combination: Combination) -> dict[str, str]:
        mapping = dict()
        assert(self.template.count_placeholder == len(combination.items))

        for var, new_var in zip(self.template.mapping, combination.items):
            mapping[var] = new_var

        return mapping 
    
    def construct_all_Combinations(self, vars: List[str]) -> List[TemplateInstance]:
        """
        Constructs all Template Instances from the possible combinations of vars given
        f.e. vars = 1,2,3
        placeholder = 2
        templates -> (1,1) (1,2) (1,3) (2,1) (2,2) (2,3) (3,1) (3,2) (3,3)
        """
        combinations = product(vars, repeat=self.template.count_placeholder)
        tmpl_instances = list()
        for combination_it in combinations:
            combination = Combination(combination_it)
            new_mapping = self.create_Mapping(combination)
            transformer = TemplateTransformer(new_mapping)
            stmt_copy = deepcopy(self.template.statement)
            new_tree = transformer.visit(stmt_copy)
            tmpl_instance = TemplateInstance(self.template, new_tree, combination, new_mapping)
            tmpl_instances.append(tmpl_instance)
        
        return tmpl_instances

class VarNamesCollector(ast.NodeVisitor):
    """
    Collects the Variable Names of the statement it is visiting.

    collector = VarCollector()
    collector.visit(stmt)
    vars = collector.vars
    """
    def __init__(self) -> None:
        self.vars = set()

    def visit_arg(self, node: ast.arg):
        if not node.arg == "self":
            self.vars.add(node.arg)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        self.vars.add(node.id)
        self.generic_visit(node)


#TODO: Scopes beachten
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
            for i in range(1, len(vars)+1):
                for combination_it in combinations_with_replacement(vars, i):
                    combination = Combination(combination_it)
                    if combination not in self.probabilities.keys():
                        same_combination, same_number_of_vars = self.checkCombination(combination)
                        try:
                            probability = same_combination / same_number_of_vars
                        except ZeroDivisionError:
                            probability = 0.0
                        self.probabilities[combination.items] = probability

    def checkCombination(self, combination: Combination) -> Tuple[int, int]:
        """
        Checks all the Statement if it contains the combination 
        or if the statment has the same number of vars as the combination
        """
        same_combination = 0
        same_number_of_vars = 0
        for statement in self.statements.values():
            visitor = VarNamesCollector()
            visitor.visit(statement)
            vars = visitor.vars
            if combination.items == set(vars):
                same_combination+=1
            
            if len(combination.items) == len(vars):
                same_number_of_vars+=1
        
        return (same_combination, same_number_of_vars)

class Scope():
    def __init__(self):
        self.vars = set()

    def add(self, var):
        self.vars.add(var)


class Scope_Constructor(ast.NodeVisitor):
    """
    Collects the variables which are in the same scope as a statement.
    Every stmt gets a list of scopes. So to get all var in scope you need to iterate over the list.
    
    constructor = Scope_Constructor()
    constructor.search(program)
    stms_with_scope = constructor.scope_stmt
    """
    def __init__(self):
        self.scope_stack: List[Scope] = list()
        self.scope_stmt: dict[ast.AST, List[Scope]] = {}
        
    def visit_Name(self, node: ast.Name):
        self.scope_stack[-1].add(node.id)
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg):
        if not node.arg == "self":
            self.scope_stack[-1].add(node.arg)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.visit_Helper(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_Helper(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.visit_Helper(node)

    def visit_Helper(self, node):
        #opening new scope
        self.scope_stack.append(Scope())
        self.generic_visit(node)
        #closing scope
        self.scope_stack.pop()

    def generic_visit(self, node: ast.AST):
        if isinstance(node, ast.stmt):
            scopes = list()
            for scope in self.scope_stack:
                scopes.append(scope)
            self.scope_stmt[node] = scopes
        super().generic_visit(node)
    
    def search(self, node):
        self.visit_Helper(node)