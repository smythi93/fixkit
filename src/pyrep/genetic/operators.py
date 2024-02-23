import abc
import ast
import copy
import os
import random
from typing import List

from pyrep.genetic import IdentifierRemover


class MutationOperator(abc.ABC, ast.NodeTransformer):
    def __init__(
        self, statement: ast.AST, file: os.PathLike, statements: List[ast.AST]
    ):
        if not hasattr(statement, "identifier"):
            raise ValueError("Target statement must have an identifier")
        self.statement = statement
        self.identifier = getattr(statement, "identifier")
        self.file = file
        self.statements = statements
        self.identifier_remover = IdentifierRemover()

    def generic_visit(self, node: ast.AST):
        if (
            hasattr(node, "identifier")
            and getattr(node, "identifier") == self.identifier
        ):
            return self.op()
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def mutate(self, tree: ast.AST) -> ast.AST:
        return self.visit(tree)

    @abc.abstractmethod
    def op(self) -> ast.AST:
        pass

    def remove_identifier(self, node: ast.AST):
        self.identifier_remover.visit(node)


class Delete(MutationOperator):
    def op(self) -> ast.AST:
        return ast.Pass()


class SelectionMutationOperator(MutationOperator, abc.ABC):
    def __init__(
        self, statement: ast.AST, file: int, statements: List[ast.AST], deepcopy=True
    ):
        super().__init__(statement, file, statements)
        self.selection = random.choice(self.statements)
        self.selection_identifier = self.selection.identifier
        if deepcopy:
            self.selection = copy.deepcopy(self.selection)
            self.remove_identifier(self.selection)


class Insert(SelectionMutationOperator, abc.ABC):
    def op(self) -> ast.AST:
        return self.insert()

    @abc.abstractmethod
    def insert(self) -> ast.AST:
        pass


class InsertBefore(Insert):
    def insert(self) -> ast.AST:
        return ast.Module(body=[self.selection, self.statement])


class InsertAfter(Insert):
    def insert(self) -> ast.AST:
        return ast.Module(body=[self.statement, self.selection])


class Replace(SelectionMutationOperator):
    def __init__(self, statement: ast.AST, file: int, statements: List[ast.AST]):
        super().__init__(statement, file, statements)
        self.selection.identifier = self.identifier

    def op(self) -> ast.AST:
        return self.selection


class OtherMutationOperator(SelectionMutationOperator, abc.ABC):
    def generic_visit(self, node):
        if (
            hasattr(node, "identifier")
            and getattr(node, "identifier") == self.selection_identifier
        ):
            return self.op_other()
        return super().generic_visit(node)

    @abc.abstractmethod
    def op_other(self) -> ast.AST:
        pass


class Move(OtherMutationOperator, abc.ABC):
    def op(self) -> ast.AST:
        return ast.Pass()


class MoveBefore(Move):
    def op_other(self) -> ast.AST:
        return ast.Module(body=[self.statement, self.selection])


class MoveAfter(Move):
    def op_other(self) -> ast.AST:
        return ast.Module(body=[self.selection, self.statement])


class Swap(OtherMutationOperator):
    def __init__(self, statement: ast.AST, file: int, statements: List[ast.AST]):
        super().__init__(statement, file, statements, deepcopy=False)

    def op(self) -> ast.AST:
        return self.selection

    def op_other(self) -> ast.AST:
        return self.statement


class Copy(MutationOperator):
    def __init__(self, statement: ast.AST, file: int, statements: List[ast.AST]):
        super().__init__(statement, file, statements)
        self.copy = copy.deepcopy(self.statement)
        self.remove_identifier(self.copy)

    def op(self) -> ast.AST:
        return ast.Module(body=[self.statement, self.copy])


class ReplaceOperand(MutationOperator):
    def op(self) -> ast.AST:
        pass


class ReplaceBinaryOperator(ReplaceOperand):
    pass


class ReplaceComparisonOperator(ReplaceOperand):
    pass


class ReplaceUnaryOperator(ReplaceOperand):
    pass


class ReplaceBooleanOperator(ReplaceOperand):
    pass


class Rename(MutationOperator):
    def op(self) -> ast.AST:
        pass
