import abc
import ast
import copy
import random
from typing import List, Dict, Optional, Set


class MutationOperator(abc.ABC):
    def __init__(self, identifier: int, choices: Optional[List[int]] = None):
        self.identifier = identifier
        self.choices = choices or list()

    @abc.abstractmethod
    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        return NotImplemented

    def __hash__(self):
        return hash((self.__class__.__name__, self.identifier))

    @abc.abstractmethod
    def __eq__(self, other):
        return NotImplemented


class Delete(MutationOperator):
    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        mutations[self.identifier] = ast.Pass()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return isinstance(other, Delete) and self.identifier == other.identifier


class SelectionMutationOperator(MutationOperator, abc.ABC):
    def __init__(self, identifier: int, choices: List[int]):
        super().__init__(identifier, choices)
        self.selection_identifier = random.choice(self.choices)


class Insert(SelectionMutationOperator, abc.ABC):
    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        mutations[self.identifier] = self.insert(
            mutations.get(self.identifier, statements[self.identifier]),
            mutations.get(
                self.selection_identifier, statements[self.selection_identifier]
            ),
        )

    @abc.abstractmethod
    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        pass


class InsertBefore(Insert):
    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        return ast.Module(body=[selection, tree], type_ignores=[])

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, InsertBefore)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class InsertAfter(Insert):
    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        return ast.Module(body=[tree, selection], type_ignores=[])

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, InsertAfter)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class InsertBoth(Insert):
    def __init__(self, identifier: int, choices: List[int]):
        super().__init__(identifier, choices)
        self.inserter = random.choice([InsertBefore, InsertAfter])

    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        return self.inserter.insert(self, tree, selection)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, InsertBoth)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
            and self.inserter == other.inserter
        )


class Replace(SelectionMutationOperator):
    def __init__(self, statement: ast.AST, statements: List[ast.AST]):
        super().__init__(statement, statements)

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        mutations[self.identifier] = mutations.get(
            self.selection_identifier, statements[self.selection_identifier]
        )

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, Replace)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class OtherMutationOperator(SelectionMutationOperator, abc.ABC):
    @abc.abstractmethod
    def mutate_this(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        pass

    @abc.abstractmethod
    def mutate_other(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        pass

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        this = mutations.get(self.identifier, statements[self.identifier])
        other = mutations.get(
            self.selection_identifier, statements[self.selection_identifier]
        )
        self.mutate_this(mutations, statements, this, other)
        self.mutate_other(mutations, statements, this, other)


class Move(OtherMutationOperator, abc.ABC):
    def mutate_this(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        mutations[self.identifier] = ast.Pass()


class MoveBefore(Move):
    def mutate_other(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        mutations[self.selection_identifier] = ast.Module(
            body=[
                this,
                other,
            ],
            type_ignores=[],
        )

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, MoveBefore)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class MoveAfter(Move):
    def mutate_other(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        mutations[self.selection_identifier] = ast.Module(
            body=[
                other,
                this,
            ],
            type_ignores=[],
        )

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, MoveAfter)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class MoveBoth(Move):
    def __init__(self, identifier: int, choices: List[int]):
        super().__init__(identifier, choices)
        self.mover = random.choice([MoveBefore, MoveAfter])

    def mutate_other(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        self.mover.mutate_other(self, mutations, statements, this, other)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, MoveBoth)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
            and self.mover == other.mover
        )


class Swap(OtherMutationOperator):
    def mutate_this(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        mutations[self.identifier] = other

    def mutate_other(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        mutations[self.selection_identifier] = this

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, Swap)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class Copy(MutationOperator):
    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        statement = mutations.get(self.identifier, statements[self.identifier])
        mutations[self.identifier] = ast.Module(
            body=[statement, statement],
            type_ignores=[],
        )

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return isinstance(other, Copy) and self.identifier == other.identifier


class ReplaceOperand(MutationOperator):
    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        pass

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return False


class ReplaceBinaryOperator(ReplaceOperand):
    pass


class ReplaceComparisonOperator(ReplaceOperand):
    pass


class ReplaceUnaryOperator(ReplaceOperand):
    pass


class ReplaceBooleanOperator(ReplaceOperand):
    pass


class Rename(MutationOperator):
    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        pass

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return False


class Mutator(ast.NodeTransformer):
    def __init__(
        self, statements: Dict[int, ast.AST], mutations: List[MutationOperator]
    ):
        self.statements = statements
        self.mutations = mutations
        self.identifier_map = dict()
        for m in self.mutations:
            m.mutate(self.identifier_map, self.statements)
        self.mutation_map = {
            self.statements[identifier]: self.identifier_map[identifier]
            for identifier in self.identifier_map
        }

    def generic_visit(self, node):
        if node in self.mutation_map:
            return self.mutation_map[node]
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

    def mutate(self, tree: ast.AST):
        return self.visit(tree)

    def get_mutation_indices(self) -> Set[int]:
        return set(self.identifier_map.keys())
