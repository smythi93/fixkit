import abc
import ast
from typing import Dict, List

from pyrep.logger import LOGGER
from pyrep.search.search import SearchStrategy, EvolutionaryStrategy
from pyrep.candidate import GeneticCandidate
from pyrep.genetic.operators import MutationOperator

class IngredientSearch(EvolutionaryStrategy, abc.ABC):

    #space ist sozusagen unsere ganzes programm für den moment aus dem wir einen passendes ingredient suchen
    @abc.abstractmethod
    def __init__(self, space: ast.AST):
        self.space = space

    #Method that returns an Ingredient from the ingredient space given a
    #statement and a Operator
    #statement gets modified using the ingredient and operator
    def getFixIngredient(statement, operator):
        pass

    #die unterscheiden zwischen local, global, package .. bei uns gibts wahrscheinlich nur local?
    def getIngredientSpace():
        pass

#warum heißt das clone .. irgendwas mit der granularity zu tun
class CloneIngredientSearch(IngredientSearch):
    def __init__(self, space: ast.AST):
        super().__init__(space)

    #get a smiliar statement to statement which than can be used for mutation
    #können auch das identifizierende int dazu 	geben, statt das statement
    def getFixIngredient(self, candidate: GeneticCandidate, statement: ast.AST, operator: MutationOperator):
        statements = candidate.statements #quasi unser Programm
        identifier = statements.
        choices = self.getSimStatements(statements, statement)
        op = operator(identifier, choices)

        
        
            #die führen jetzt hier auch gleich die transformierung durch
            #und returnen dann das transformierte ingredient

    #die machen das mit einer distanz matrix die sie irgendwie laden, haben wir nicht was können wir stattdessen machen
    def getSimStatements(self, statements: Dict[int, ast.AST], statement: ast.AST) -> List[int]:
