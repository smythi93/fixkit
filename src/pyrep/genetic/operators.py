import abc
import ast
import copy
import os
import random
from typing import List, Dict, Optional


class IdentifierRemover(ast.NodeVisitor):
    def generic_visit(self, node):
        if hasattr(node, "identifier"):
            delattr(node, "identifier")
        return super().generic_visit(node)


class MutationOperator(abc.ABC, ast.NodeTransformer):
    def __init__(
        self, identifier: int, file: os.PathLike, choices: Optional[List[int]] = None
    ):
        self.identifier = identifier
        self.file = file
        self.choices = choices or list()
        self.identifier_remover = IdentifierRemover()
        self.statements: Dict[int, ast.AST] = dict()

    def generic_visit(self, node: ast.AST):
        if (
            hasattr(node, "identifier")
            and getattr(node, "identifier") == self.identifier
        ):
            return self.op()
        node = copy.copy(node)
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
                setattr(node, field, new_values)
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def mutate(self, tree: ast.AST, statements: Dict[int, ast.AST]) -> ast.AST:
        self.statements = statements
        return self.visit(tree)

    @abc.abstractmethod
    def op(self) -> ast.AST:
        pass

    def remove_identifier(self, node: ast.AST):
        self.identifier_remover.visit(node)


class Delete(MutationOperator):
    def __init__(
        self, identifier: int, file: os.PathLike, choices: Optional[List[int]] = None
    ):
        super().__init__(identifier, file, choices)
        self.pass_stmt = ast.Pass()
        self.pass_stmt.identifier = self.identifier

    def op(self) -> ast.AST:
        self.statements[self.identifier] = self.pass_stmt
        return self.pass_stmt


class SelectionMutationOperator(MutationOperator, abc.ABC):
    def __init__(self, identifier: int, file: os.PathLike, choices: List[int]):
        super().__init__(identifier, file, choices)
        self.selection_identifier = random.choice(self.choices)


class Insert(SelectionMutationOperator, abc.ABC):
    def op(self) -> ast.AST:
        selection = copy.deepcopy(self.statements[self.selection_identifier])
        self.remove_identifier(selection)
        return self.insert(selection)

    @abc.abstractmethod
    def insert(self, selection: ast.AST) -> ast.AST:
        pass


class InsertBefore(Insert):
    def insert(self, selection: ast.AST) -> ast.AST:
        return ast.Module(
            body=[selection, self.statements[self.identifier]], type_ignores=[]
        )


class InsertAfter(Insert):
    def insert(self, selection: ast.AST) -> ast.AST:
        return ast.Module(
            body=[self.statements[self.identifier], selection], type_ignores=[]
        )


class Replace(SelectionMutationOperator):
    def __init__(self, statement: ast.AST, file: int, statements: List[ast.AST]):
        super().__init__(statement, file, statements)

    def op(self) -> ast.AST:
        selection = copy.deepcopy(self.statements[self.selection_identifier])
        self.remove_identifier(selection)
        selection.identifier = self.identifier
        self.statements[self.identifier] = selection
        return selection


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
        return ast.Module(
            body=[
                self.statements[self.identifier],
                self.statements[self.selection_identifier],
            ],
            type_ignores=[],
        )


class MoveAfter(Move):
    def op_other(self) -> ast.AST:
        return ast.Module(
            body=[
                self.statements[self.selection_identifier],
                self.statements[self.identifier],
            ],
            type_ignores=[],
        )


class Swap(OtherMutationOperator):
    def __init__(self, statement: ast.AST, file: int, choices: List[ast.AST]):
        super().__init__(statement, file, choices)

    def op(self) -> ast.AST:
        return self.statements[self.selection_identifier]

    def op_other(self) -> ast.AST:
        return self.statements[self.identifier]


class Copy(MutationOperator):
    def __init__(
        self, statement: ast.AST, file: int, choices: Optional[List[int]] = None
    ):
        super().__init__(statement, file, choices)

    def op(self) -> ast.AST:
        copied_stmt = copy.deepcopy(self.statements[self.identifier])
        self.remove_identifier(copied_stmt)
        return ast.Module(
            body=[self.statements[self.identifier], copied_stmt], type_ignores=[]
        )


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
