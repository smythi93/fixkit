import ast
from typing import Set, Dict, Optional, List


class Scope:
    def __init__(self, parent: Optional["Scope"] = None, sub: bool = False):
        self.parent = parent
        self.defs: Dict[str, ast.AST] = dict()
        self.children = list()
        self.sub = sub

    def __getitem__(self, name: str) -> List[ast.AST]:
        defs = []
        if name in self.defs:
            defs.append(self.defs[name])
            if self.sub and self.parent:
                defs.extend(self.parent[name])
        elif self.parent:
            return self.parent[name]
        raise KeyError(name)

    def __setitem__(self, name: str, value: ast.AST):
        self.defs[name] = value

    def __contains__(self, item: str) -> bool:
        if item in self.defs:
            return True
        if self.parent:
            return item in self.parent
        return False

    def get_variables(self) -> Set[str]:
        return (
            (set(self.defs.keys()) | self.parent.get_variables())
            if self.parent
            else set(self.defs.keys())
        )

    def enter(self, sub: bool = False) -> "Scope":
        child = Scope(self, sub=sub)
        self.children.append(child)
        return child

    def exit(self) -> "Scope":
        if self.parent:
            if self.sub and self.parent.sub:
                return self.parent.exit()
            return self.parent
        return self
