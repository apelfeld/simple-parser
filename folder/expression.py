import typing
import enum
from front.ast import Expression


class ConstantKind(enum.IntEnum):
    Bool = enum.auto()
    Int = enum.auto()
    Float = enum.auto()
    String = enum.auto()


class UnaryOperatorKind(enum.IntEnum):
    Negate = enum.auto()
    Posate = enum.auto()
    Flip = enum.auto()
    Invert = enum.auto()


class BinaryOperatorKind(enum.IntEnum):
    Add = enum.auto()
    Subtract = enum.auto()
    Multiply = enum.auto()
    Divide = enum.auto()
    Modulo = enum.auto()
    Bitand = enum.auto()
    Bitor = enum.auto()
    Bitxor = enum.auto()
    LShift = enum.auto()
    RShift = enum.auto()

    CmpGreater = enum.auto()
    CmpGreaterEqual = enum.auto()
    CmpLesser = enum.auto()
    CmpLesserEqual = enum.auto()
    CmpEqual = enum.auto()
    CmpInEqual = enum.auto()





class Constant(Expression):
    kind: ConstantKind
    value: typing.Any

    __slots__ = "kind", "value"

    def __init__(self, k: ConstantKind, v: typing.Any):
        super().__init__()
        self.kind = k
        self.value = v

    def __repr__(self):
        return repr(self.value)


class Identifier(Expression):
    name: str

    __slots__ = "name"

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self):
        return self.name


class UnaryOperator(Expression):
    operator: UnaryOperatorKind
    expr: Expression

    __slots__ = "operator", "expr"

    operator_strings: dict[UnaryOperatorKind, str] = {
        UnaryOperatorKind.Negate: "-", UnaryOperatorKind.Posate: "+",
        UnaryOperatorKind.Flip: "!", UnaryOperatorKind.Invert: "~"
    }

    def __init__(self, operator: UnaryOperatorKind, expr: Expression):
        super().__init__()
        self.expr = expr
        self.operator = operator

    def __repr__(self):
        return f"{self.operator_strings[self.operator]}{self.expr}"


class BinaryOperator(Expression):
    operator: BinaryOperatorKind
    lhs: Expression
    rhs: Expression

    __slots__ = "lhs", "rhs", "operator"

    operator_strings: dict[BinaryOperatorKind, str] = {
        BinaryOperatorKind.Add: "+", BinaryOperatorKind.Subtract: "-",
        BinaryOperatorKind.Multiply: "*", BinaryOperatorKind.Divide: "/",
        BinaryOperatorKind.Modulo: "%", BinaryOperatorKind.Bitand: "&",
        BinaryOperatorKind.Bitxor: "^", BinaryOperatorKind.Bitor: "|",
        BinaryOperatorKind.LShift: "<<", BinaryOperatorKind.RShift: ">>",
        BinaryOperatorKind.CmpGreater: ">", BinaryOperatorKind.CmpGreaterEqual: ">=",
        BinaryOperatorKind.CmpLesser: "<", BinaryOperatorKind.CmpLesserEqual: "<=",
        BinaryOperatorKind.CmpEqual: "==", BinaryOperatorKind.CmpInEqual: "!="
    }

    def __init__(self, lhs: Expression, operator: BinaryOperatorKind, rhs: Expression):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def __repr__(self):
        return f"({self.lhs} {self.operator_strings[self.operator]} {self.rhs})"


class TernaryOperator(Expression):
    condition: Expression
    if_clause: Expression
    else_clause: Expression

    __slots__ = "condition", "if_clause", "else_clause"

    def __init__(self, cond: Expression, if_: Expression, else_: Expression):
        self.condition = cond
        self.if_clause = if_
        self.else_clause = else_

    def __repr__(self):
        return f"({self.if_clause} if {self.condition} else {self.else_clause})"








