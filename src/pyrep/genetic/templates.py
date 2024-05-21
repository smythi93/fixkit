from _ast import Name
import ast
from typing import Any

#Problems: Python not type based -> dadurch templates oft quatsch
#In Java werden double nur durch doubles ersetzt

#Können wir uns eigentlich sparen da Rename Operator eigentlich genau das alles macht

#möglichst viele usecases abdecken -> da noch unsicher wie später nutzen
#just storage
#speichern wie viele placeholder

class Template:
    def __init__(self, statement: ast.AST) -> None:
        self.statement = statement
        self.createTemplate()

    def createTemplate(self):
        self.template = CreateTemplate().visit(self.statement)
        pass
    
    #Vor Nutzung von applyChanges ScopeVariablen Collector benutzen -> Anzahl von Placeholdern in ProbalisticModel -> Und dann in applyChanges
    def applyChanges(self):
        pass

    def getChangedStatement(self):
        pass

class CreateTemplate(ast.NodeTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        #TODO: falls es eine var öfter in einem statement gibt -> immer gleicher placeholder
        #self.translator = {a : var_1}

    def visit_Name(self, node: Name) -> Any:
        if isinstance(node.ctx, ast.Store):
            node.id = "var_" + self.count
            self.count=+1
            return node
        else: 
            return node

class ProbalisticModel:
    pass

