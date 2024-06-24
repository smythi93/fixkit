"""
The operators module provides the necessary tools to perform mutation operations on statements.
"""

import abc
import ast
import copy
import random
from typing import List, Dict, Optional, Set, Type


class MutationOperator(abc.ABC):
    """
    Abstract class for mutation operators.
    """

    def __init__(self, identifier: int, choices: Optional[List[int]] = None):
        """
        Initialize the mutation operator.
        :param int identifier: The identifier of the statement to mutate.
        :param Optional[List[int]] choices: The list of identifiers to choose from for the mutation.
        """
        self.identifier = identifier
        self.choices = choices or list()

    @abc.abstractmethod
    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        """
        Abstract method for mutating the statements, by changing the mutations' dictionary.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        """
        return NotImplemented

    def __hash__(self):
        """
        Hash the mutation operator.
        :return: The hash of the mutation operator based on the class name and identifier.
        """
        return hash((self.__class__.__name__, self.identifier))

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        """
        Abstract method for comparing the mutation operator with another.
        :param other: The other mutation operator to compare with.
        :return bool: True if the mutation operators are equal, False otherwise.
        """
        return NotImplemented


class Delete(MutationOperator):
    """
    Mutation operator for deleting a statement.
    """

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        """
        Mutate the statements by deleting the statement with the identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        """
        mutations[self.identifier] = ast.Pass()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return isinstance(other, Delete) and self.identifier == other.identifier


class SelectionMutationOperator(MutationOperator, abc.ABC):
    """
    Abstract class for selection mutation operators that leverages another statement based on choices.
    """

    def __init__(self, identifier: int, choices: List[int]):
        """
        Initialize the selection mutation operator.
        :param int identifier: The identifier of the statement to mutate.
        :param Optional[List[int]] choices: The list of identifiers to choose from for the mutation.
        """
        super().__init__(identifier, choices)
        self.selection_identifier = random.choice(self.choices)


class Insert(SelectionMutationOperator, abc.ABC):
    """
    Abstract class for insertion mutation operators that insert a statement before or after another statement.
    """

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        """
        Mutate the statements by inserting the statement with the identifier before or after the selection identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        """
        mutations[self.identifier] = self.insert(
            mutations.get(self.identifier, statements[self.identifier]),
            mutations.get(
                self.selection_identifier, statements[self.selection_identifier]
            ),
        )

    @abc.abstractmethod
    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        """
        Abstract method for inserting the selection before or after the tree.
        :param ast.Ast tree: The tree to insert the selection.
        :param ast.Ast selection: The statement to insert.
        :return: The tree with the selection inserted before or after the tree.
        """
        pass


class InsertBefore(Insert):
    """
    Mutation operator for inserting a statement before another statement.
    """

    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        """
        Insert the selection before the tree.
        :param ast.Ast tree: The tree to insert the selection.
        :param ast.Ast selection: The statement to insert.
        :return: The tree with the selection inserted before the tree.
        """
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
    """
    Mutation operator for inserting a statement after another statement.
    """

    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        """
        Insert the selection after the tree.
        :param ast.Ast tree: The tree to insert the selection.
        :param ast.Ast selection: The statement to insert.
        :return: The tree with the selection inserted after the tree.
        """
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
    """
    Mutation operator for inserting a statement before or after another statement.
    """

    def __init__(self, identifier: int, choices: List[int]):
        """
        Initialize the insert both mutation operator.
        :param int identifier: The identifier of the statement to mutate.
        :param List[int] choices: The list of identifiers to choose from for the mutation.
        """
        super().__init__(identifier, choices)
        # Choose the inserter to insert before or after the selection.
        self.inserter = random.choice([InsertBefore, InsertAfter])

    def insert(self, tree: ast.AST, selection: ast.AST) -> ast.AST:
        """
        Insert the selection before or after the tree based on the inserter chosen.
        :param ast.Ast tree: The tree to insert the selection.
        :param ast.Ast selection: The statement to insert.
        :return: The tree with the selection inserted before or after the tree.
        """
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
    """
    Mutation operator for replacing a statement with another statement.
    """

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        """
        Mutate the statements by replacing the statement of the identifier with the statement of the selection
        identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        """
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
    """
    Abstract class for mutation that mutate both the statement given by the identifier and another statement given by
    the selection.
    """

    @abc.abstractmethod
    def mutate_identifier(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Abstract method for mutating the statement given by the identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
        pass

    @abc.abstractmethod
    def mutate_selection(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Abstract method for mutating the statement given by the selection identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
        pass

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        """
        Mutate the statements by mutating the statement given by the identifier and the statement given by the
        selection.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        """
        # Get the statement of the identifier and the statement of the selection identifier with the current mutations
        # or the statements as default.
        this = mutations.get(self.identifier, statements[self.identifier])
        other = mutations.get(
            self.selection_identifier, statements[self.selection_identifier]
        )
        self.mutate_identifier(mutations, statements, this, other)
        self.mutate_selection(mutations, statements, this, other)


class Move(OtherMutationOperator, abc.ABC):
    """
    Abstract class for moving a statement before or after another statement.
    """

    def mutate_selection(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Mutate the statement given by the selection identifier by deleting it.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
        mutations[self.selection_identifier] = ast.Pass()

    def move(
        self,
        body: List[ast.AST],
        mutations: Dict[int, ast.AST],
    ):
        """
        Create a module based on the new body.
        :param List[ast.AST] body: The list of statements to move the selection identifier before or after the
        identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        """
        mutations[self.identifier] = ast.Module(
            body=body,
            type_ignores=[],
        )


class MoveBefore(Move):
    """
    Mutation operator for moving a statement before another statement.
    """

    def mutate_identifier(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Mutate the statement given by the identifier by moving the statement given by the selection identifier before
        it.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
        self.move([other, this], mutations)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, MoveBefore)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class MoveAfter(Move):
    """
    Mutation operator for moving a statement after another statement.
    """

    def mutate_identifier(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Mutate the statement given by the identifier by moving the statement given by the selection identifier after
        it.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
        self.move([this, other], mutations)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return (
            isinstance(other, MoveAfter)
            and self.identifier == other.identifier
            and self.selection_identifier == other.selection_identifier
        )


class MoveBoth(Move):
    """
    Mutation operator for moving a statement before or after another statement.
    """

    def __init__(self, identifier: int, choices: List[int]):
        """
        Initialize the move both mutation operator.
        :param int identifier: The identifier of the statement to mutate.
        :param List[int] choices: The list of identifiers to choose from for the mutation.
        """
        super().__init__(identifier, choices)
        # Choose the mover to move the selection identifier before or after the identifier.
        self.mover: Type[Move] = random.choice([MoveBefore, MoveAfter])

    def mutate_identifier(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Mutate the statement given by the identifier by moving the statement given by the selection identifier before or
        after it based on the mover chosen.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
        self.mover.mutate_identifier(self, mutations, statements, this, other)

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
    """
    Mutation operator for swapping a statement with another statement.
    """

    def mutate_identifier(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Mutate the statement given by the identifier by swapping it with the statement given by the selection
        identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
        mutations[self.identifier] = other

    def mutate_selection(
        self,
        mutations: Dict[int, ast.AST],
        statements: Dict[int, ast.AST],
        this: ast.AST,
        other: ast.AST,
    ):
        """
        Mutate the statement given by the selection identifier by swapping it with the statement given by the
        identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        :param ast.AST this: The statement of the identifier.
        :param ast.AST other: The statement of the selection identifier.
        """
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
    """
    Mutation operator for copying a statement.
    """

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        """
        Mutate the statements by copying the statement with the identifier.
        :param Dict[int, ast.AST] mutations: The dictionary of mutations to apply to the statements.
        :param Dict[int, ast.AST] statements: The dictionary of original statements if needed for mutating.
        """
        statement = mutations.get(self.identifier, statements[self.identifier])
        mutations[self.identifier] = ast.Module(
            body=[statement, statement],
            type_ignores=[],
        )

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return isinstance(other, Copy) and self.identifier == other.identifier


class ReplaceOperator(MutationOperator):
    """
    Mutation operator for replacing an operand in a statement.
    """

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        pass

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return False


class ReplaceBinaryOperator(ReplaceOperator):
    """
    Mutation operator for replacing a binary operator in a statement.
    """

    pass


class ReplaceComparisonOperator(ReplaceOperator):
    """
    Mutation operator for replacing a comparison operator in a statement.
    """

    pass


class ReplaceUnaryOperator(ReplaceOperator):
    """
    Mutation operator for replacing a unary operator in a statement.
    """

    pass


class ReplaceBooleanOperator(ReplaceOperator):
    """
    Mutation operator for replacing a boolean operator in a statement.
    """

    pass


class Rename(MutationOperator):
    """
    Mutation operator for renaming an identifier in a statement.
    """

    def mutate(self, mutations: Dict[int, ast.AST], statements: Dict[int, ast.AST]):
        pass

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return False


class Mutator(ast.NodeTransformer):
    """
    Mutator class to mutate the abstract syntax tree based on the mutation operators.
    """

    def __init__(
        self, statements: Dict[int, ast.AST], mutations: List[MutationOperator]
    ):
        """
        Initialize the mutator.
        :param Dict[int, ast.AST] statements: The dictionary of original statements used for mutating.
        :param List[MutationOperator] mutations: The list of mutation operators to apply to the statements.
        """
        self.statements = statements
        self.mutations = mutations
        # Create a map of the mutations.
        self.identifier_map = dict()
        for m in self.mutations:
            m.mutate(self.identifier_map, self.statements)
        self.mutation_map = {
            self.statements[identifier]: self.identifier_map[identifier]
            for identifier in self.identifier_map
        }

    def generic_visit(self, node: ast.AST) -> ast.AST:
        """
        Visit the node and mutate it based on the mutation map.
        :param ast.AST node: The node to visit and mutate.
        :return ast.AST: The mutated node.
        """
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

    def mutate(self, tree: ast.AST) -> ast.AST:
        """
        Mutate the abstract syntax tree based on the mutation operators.
        :param ast.AST tree: The abstract syntax tree to mutate.
        :return ast.AST: The mutated abstract syntax tree.
        """
        return self.visit(tree)

    def get_mutation_indices(self) -> Set[int]:
        """
        Get the set of mutation indices, i.e., the statements that will get mutated.
        :return Set[int]: The set of mutation indices.
        """
        return set(self.identifier_map.keys())


__all__ = [
    "MutationOperator",
    "Delete",
    "InsertAfter",
    "InsertBefore",
    "InsertBoth",
    "Replace",
    "MoveAfter",
    "MoveBefore",
    "MoveBoth",
    "Swap",
    "Copy",
    "Mutator",
]
