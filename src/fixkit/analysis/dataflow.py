import ast
from typing import Dict, List

from fixkit.analysis.scope import Scope


class VariableExtractor(ast.NodeVisitor):
    def __init__(self):
        self.variables = set()

    def visit_Name(self, node):
        self.variables.add(node.id)

    def search(self, node):
        self.variables.clear()
        self.generic_visit(node)
        return self.variables


class DataflowAnalysis(ast.NodeVisitor):
    def __init__(self):
        self.def_uses: Dict[ast.AST, List[ast.AST]] = dict()
        self.scope = Scope()
        self.variable_extractor = VariableExtractor()

    def visit_scope(self, node: ast.AST):
        self.scope = self.scope.enter()
        self.generic_visit(node)

    def visit_sub_scope(self, nodes: List[ast.AST]):
        self.scope = self.scope.enter(sub=True)
        for node in nodes:
            self.visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.visit_scope(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_scope(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.visit_scope(node)

    def visit_use(self, node: ast.expr):
        for var in self.variable_extractor.search(node):
            if var in self.scope:
                for def_ in self.scope[var]:
                    self.def_uses[def_].append(node)

    def visit_Assign(self, node: ast.Assign):
        self.visit_use(node.value)
        for target in node.targets:
            for var in self.variable_extractor.search(target):
                self.scope[var] = node
                self.def_uses[node] = []
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        self.visit_use(node.value)
        self.visit_use(node.target)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        self.visit_use(node.value)
        for var in self.variable_extractor.search(node.target):
            self.scope[var] = node
            self.def_uses[node] = []

    def visit_For(self, node: ast.For):
        self.visit_use(node.iter)
        for var in self.variable_extractor.search(node.target):
            self.scope[var] = node
            self.def_uses[node] = []
        self.visit_sub_scope(node.body)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self.visit_For(node)

    def visit_With(self, node: ast.With):
        self.visit_use(node.context_expr)
        for var in self.variable_extractor.search(node.optional_vars):
            self.scope[var] = node
            self.def_uses[node] = []
        self.visit_sub_scope(node.body)

    def visit_AsyncWith(self, node: ast.AsyncWith):
        self.visit_With(node)

    def visit_Expr(self, node: ast.Expr):
        self.visit_use(node)

    def visit_Return(self, node: ast.Return):
        self.visit_use(node)

    def visit_Delete(self, node: ast.Delete):
        self.visit_use(node)

    def visit_Raise(self, node: ast.Raise):
        self.visit_use(node)

    def visit_Yield(self, node: ast.Yield):
        self.visit_use(node)

    def visit_YieldFrom(self, node: ast.YieldFrom):
        self.visit_use(node)

    def visit_If(self, node: ast.If):
        self.visit_use(node.test)
        self.visit_sub_scope(node.body)
        self.visit_sub_scope(node.orelse)

    def visit_Match(self, node: ast.Match):
        self.visit_use(node.subject)
        for case in node.cases:
            self.visit_use(case.pattern)
            self.visit_sub_scope(case.body)

    def visit_Assert(self, node: ast.Assert):
        self.visit_use(node.test)
        self.visit_use(node.msg)

    def visit_Try(self, node: ast.Try):
        self.visit_sub_scope(node.body)
        for handler in node.handlers:
            self.visit_use(handler.type)
            self.visit_sub_scope(handler.body)
        self.visit_sub_scope(node.orelse)
        self.visit_sub_scope(node.finalbody)

    def visit_TryStar(self, node: ast.TryStar):
        self.visit_sub_scope(node.body)
        for handler in node.handlers:
            self.visit_use(handler.type)
            self.visit_sub_scope(handler.body)
        self.visit_sub_scope(node.orelse)
        self.visit_sub_scope(node.finalbody)

    def analyze(self, node: ast.AST):
        self.def_uses.clear()
        self.visit(node)
        return self.def_uses
