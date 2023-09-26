from dataclasses import dataclass
from front.token import Token, TokenType, Tokenizer, UnknownCharacterError
from front.ast import Expression, Statement, AstNode
from front.expression import *
from front.statement import *
from front.types import *
from collections import namedtuple
import enum



class SymbolEntryKind(enum.IntEnum):
    Variable = enum.auto()
    Type = enum.auto()


@dataclass
class SymbolEntry:
    kind: SymbolEntryKind
    type: QualifiedType

    __slots__ = "kind", "type"


@dataclass
class OpInfo:
    precedence: int
    left_associativity: bool
    kind: BinaryOperatorKind

    __slots__ = "precedence", "left_associativity", "kind"




class Parser:

    operator_map = {
        TokenType.Star: OpInfo(0, True, BinaryOperatorKind.Multiply),
        TokenType.Slash: OpInfo(0, True, BinaryOperatorKind.Divide),
        TokenType.Percent: OpInfo(0, True, BinaryOperatorKind.Modulo),

        TokenType.Plus: OpInfo(-1, True, BinaryOperatorKind.Add),
        TokenType.Minus: OpInfo(-1, True, BinaryOperatorKind.Subtract),

        TokenType.LShift: OpInfo(-2, True, BinaryOperatorKind.LShift),
        TokenType.RShift: OpInfo(-2, True, BinaryOperatorKind.RShift),

        TokenType.Greater: OpInfo(-3, True, BinaryOperatorKind.CmpGreater),
        TokenType.GreaterEqual: OpInfo(-3, True, BinaryOperatorKind.CmpGreaterEqual),
        TokenType.Lesser: OpInfo(-3, True, BinaryOperatorKind.CmpLesser),
        TokenType.LesserEqual: OpInfo(-3, True, BinaryOperatorKind.CmpLesserEqual),

        TokenType.Equal: OpInfo(-4, True, BinaryOperatorKind.CmpEqual),
        TokenType.BangEqual: OpInfo(-4, True, BinaryOperatorKind.CmpInEqual),

        TokenType.Ampersand: OpInfo(-5, True, BinaryOperatorKind.Bitand),
        TokenType.Caret: OpInfo(-6, True, BinaryOperatorKind.Bitxor),
        TokenType.Pipe: OpInfo(-7, True, BinaryOperatorKind.Bitor),
    }

    source_code: str
    tokenizer: Tokenizer
    token: Token
    errors: list[str]
    symbol_table: list[dict[str, SymbolEntry]]

    __slots__ = "source_code", "tokenizer", "token", "errors", "symbol_table", "void_type"

    def __init__(self, text: str):
        self.source_code = text
        self.tokenizer = Tokenizer(text)
        self.token = self.tokenizer()
        self.errors = []
        self.void_type = QualifiedType(VoidType())
        self.symbol_table = [{}]
        self.symbol_table[-1]["i32"] = SymbolEntry(SymbolEntryKind.Type, QualifiedType(IntegerType(32), 0))


    def search_symbol(self, key: str) -> typing.Optional[SymbolEntry]:
        for d in reversed(self.symbol_table):
            e: SymbolEntry = d.get(key, None)
            if e is not None:
                return e
        return None

    def enter_scope(self):
        self.symbol_table.append({})

    def leave_scope(self):
        self.symbol_table.pop()

    def advance(self) -> Token:
        t: Token = self.token
        self.token = self.tokenizer()
        return t

    def match(self, tp: TokenType) -> bool:
        if self.token.type == tp:
            self.token = self.tokenizer()
            return True
        else:
            return False

    def consume(self, t: TokenType, s: str) -> bool:
        if self.token.type == t:
            self.token = self.tokenizer()
            return True
        else:
            self.errors.append(s)
            return False

    def parse_parenthesis(self) -> Expression:
        e: Token = self.parse_expression()
        self.consume(TokenType.RParen, "Expected ')' after expression in parenthesis")
        return e

    def parse_atom(self) -> Expression:
        token: Token = self.token
        if self.match(TokenType.Identifier):
            return Identifier(token.value)
        elif self.match(TokenType.IntLiteral):
            return Constant(ConstantKind.Int, token.value)
        elif self.match(TokenType.StringLiteral):
            return Constant(ConstantKind.String, token.value)
        elif self.match(TokenType.Minus):
            return UnaryOperator(UnaryOperatorKind.Negate, self.parse_atom())
        elif self.match(TokenType.Plus):
            return UnaryOperator(UnaryOperatorKind.Posate, self.parse_atom())
        elif self.match(TokenType.Bang):
            return UnaryOperator(UnaryOperatorKind.Flip, self.parse_atom())
        elif self.match(TokenType.Tilde):
            return UnaryOperator(UnaryOperatorKind.Invert, self.parse_atom())
        elif self.match(TokenType.LParen):
            return self.parse_parenthesis()

    def parse_expression(self, min_prec: int = -1000) -> Expression:
        lhs: Expression = self.parse_atom()

        while self.token.type in self.operator_map:
            if self.operator_map[self.token.type].precedence < min_prec:
                break

            info = self.operator_map[self.token.type]
            self.advance()
            next_prec = info.precedence + int(info.left_associativity)
            rhs = self.parse_expression(next_prec)
            lhs = BinaryOperator(lhs, info.kind, rhs)

        return lhs

    def parse_block(self) -> Statement:
        statements: list[Statement] = []
        while not self.match(TokenType.RBrace):
            statements.append(self.parse_statement())
        return StatementBlock(statements)

    def parse_if(self) -> Statement:
        self.consume(TokenType.LParen, "Expected '(' after if statement")
        condition = self.parse_expression()
        self.consume(TokenType.RParen, "Expected ')' after if's condition")
        if_clause = self.parse_statement()
        else_clause = None
        if self.match(TokenType.ElseKW):
            else_clause = self.parse_statement()

        return IfStatement(condition, if_clause, else_clause)
    
    def parse_type_expression(self) -> QualifiedType:
        name: str = self.token.value
        self.consume(TokenType.Identifier, "Type must be an identifier")
        entry: SymbolEntry = self.search_symbol(name)
        if entry is None:
            self.errors.append(f"No type found with name {name}")
            return self.void_type
        elif entry.kind != SymbolEntryKind.Type:
            self.errors.append("Non-type symbol used as a type expression")
            return self.void_type

        if self.match(TokenType.Ampersand):
            return entry.type.add_flags(QualifiedType.Reference)
        else:
            return entry.type

    def parse_variable_declaration(self) -> VariableDeclaration:
        name = self.token.value
        self.consume(TokenType.Identifier, "Variable declaration must have a name!")
        self.consume(TokenType.Colon, "Expected ':' after variable declaration name")
        tp = self.parse_type_expression()
        init: Expression = None
        if self.match(TokenType.Equal):
            init = self.parse_expression()
        self.consume(TokenType.Semicolon, "Expected ';' after variable declaration")
        return VariableDeclaration(name, tp, init)

    def parse_function_definition(self) -> FunctionDefinition:
        name = self.token.value
        arg_names = []
        arg_types = []

        self.consume(TokenType.Identifier, "Function definition must have a name!")
        self.consume(TokenType.LParen, "Expected '(' after function name")

        while self.token.type == TokenType.Identifier:
            arg_name = self.advance().value
            self.consume(TokenType.Colon, "Expected ':' after function parameter name")
            arg_type = self.parse_type_expression()
            arg_names.append(arg_name)
            arg_types.append(arg_type)
            if not self.match(TokenType.Comma):
                break

        self.consume(TokenType.RParen, "Expected ')' after function arguments")
        self.consume(TokenType.Arrow, "Expected '->' after function arguments")
        ret_tp = self.parse_type_expression()
        func_type = FunctionType(ret_tp, arg_types)
        if self.match(TokenType.Semicolon):
            return FunctionDefinition(name, func_type, arg_names, None)
        else:
            self.consume(TokenType.LBrace, "Expected '{' after function definition")
            code = self.parse_block()
            return FunctionDefinition(name, func_type, arg_names, code)


    def parse_statement(self) -> Statement:

        if self.match(TokenType.ReturnKW):
            stmt: Statement = ReturnStatement(self.parse_expression())
            self.consume(TokenType.Semicolon, "Expected ';' after return statement")
            return stmt
        elif self.match(TokenType.FnKW):
            return self.parse_function_definition()
        elif self.match(TokenType.VarKW):
            return self.parse_variable_declaration()
        elif self.match(TokenType.IfKW):
            return self.parse_if()
        elif self.match(TokenType.LBrace):
            return self.parse_block()
        else:
            stmt: Statement = ExpressionStatement(self.parse_expression())
            self.consume(TokenType.Semicolon, "Expected ';' after expression statement")
            return stmt

    def parse_module(self) -> ModuleDefinition:
        statements: list[Statement] = []
        while self.token.type != TokenType.EndOfFile:
            stmt = self.parse_statement()
            statements.append(stmt)
        return ModuleDefinition(statements)