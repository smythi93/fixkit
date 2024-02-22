class Operator:
    pass


class Delete(Operator):
    pass


class Insert(Operator):
    pass


class InsertBefore(Insert):
    pass


class InsertAfter(Insert):
    pass


class Replace(Operator):
    pass


class Move(Operator):
    pass


class Swap(Operator):
    pass


class Copy(Operator):
    pass


class ReplaceOperand(Operator):
    pass


class ReplaceBinaryOperator(ReplaceOperand):
    pass


class ReplaceComparisonOperator(ReplaceOperand):
    pass


class ReplaceUnaryOperator(ReplaceOperand):
    pass


class ReplaceBooleanOperator(ReplaceOperand):
    pass


class Rename(Operator):
    pass
