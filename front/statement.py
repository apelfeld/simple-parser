import enum
import typing
from front.ast import Expression, Statement
from front.types import QualifiedType, UnqualifiedType, FunctionType





class ExpressionStatement(Statement):
    expr: Expression

    __slots__ = "expr"

    def __init__(self, e: Expression):
        super().__init__()
        self.expr = e

    def __repr__(self):
        return f"{self.expr};"


class ReturnStatement(Statement):
    expr: Expression

    __slots__ = "expr"

    def __init__(self, e: Expression):
        super().__init__()
        self.expr = e

    def __repr__(self):
        return f"return {self.expr};"


class StatementBlock(Statement):
    statements: list[Statement]

    __slots__ = "statements"

    def __init__(self, statements: list[Statement]):
        super().__init__()
        self.statements = statements

    def __repr__(self):
        strings: list[str] = [repr(x) for x in self.statements]
        strings = ["\n    ".join(s.split("\n")) for s in strings]
        string: str = "\n    ".join(strings)
        return f"{{\n    {string}\n}}"


class IfStatement(Statement):
    condition: Expression
    if_clause: Statement
    else_clause: Statement

    __slots__ = "condition", "if_clause", "else_clause"

    def __init__(self, cond: Expression, if_: Statement, else_: Statement):
        super().__init__()
        self.condition = cond
        self.if_clause = if_
        self.else_clause = else_

    def __repr__(self):
        s: str = f"if({self.condition}) {self.if_clause}"
        if self.else_clause is not None:
            s += f"\nelse {self.else_clause}"
        return s


class VariableDeclaration(Statement):
    name: str
    qualified_type: QualifiedType
    initializer: Expression

    __slots__ = "name", "qualified_type", "initializer"

    def __init__(self, name: str, tp: QualifiedType, initializer: Expression = None):
        super().__init__()
        self.name = name
        self.qualified_type = tp
        self.initializer = initializer

    def __repr__(self):
        s = f"var {self.name}: {self.qualified_type}"
        if self.initializer is not None:
            return s + f" = {self.initializer};"
        else:
            return s + ";"


class FunctionDefinition(Statement):
    name: str
    function_type: FunctionType
    arg_names: list[str]
    code: StatementBlock

    __slots__ = "name", "function_type", "arg_names", "code"

    def __init__(self, name: str, tp: FunctionType, names: list[str], code: StatementBlock):
        self.name = name
        self.function_type = tp
        self.arg_names = names
        self.code = code

        assert len(self.function_type.arguments) == len(self.arg_names)
        assert self.code is None or isinstance(self.code, StatementBlock)

    def __repr__(self):
        s: str =  f"fn {self.name}("\
                  + ", ".join(f"{arg}: {tp}" for arg, tp in zip(self.arg_names, self.function_type.arguments))\
                  + f") -> {self.function_type.return_type} "
        if self.code is not None:
            return s + repr(self.code)
        else:
            return s + ";"


class ModuleDefinition(Statement):
    statements: list[Statement]

    __slots__ = "statements",

    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def __repr__(self):
        return "\n".join(repr(x) for x in self.statements)


__all__ = ["ExpressionStatement", "ReturnStatement", "IfStatement",
           "StatementBlock", "VariableDeclaration", "FunctionDefinition",
           "ModuleDefinition"]
