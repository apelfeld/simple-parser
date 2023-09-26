from enum import IntEnum
from dataclasses import dataclass
from string import ascii_letters, digits as ascii_digits
import typing
import enum
import sys



class TokenType(IntEnum):
    Error = enum.auto()
    EndOfFile = enum.auto()

    LParen = enum.auto()
    RParen = enum.auto()
    LBrace = enum.auto()
    RBrace = enum.auto()
    LBracket = enum.auto()
    RBracket = enum.auto()

    Comma = enum.auto()
    Dot = enum.auto()
    Semicolon = enum.auto()
    Colon = enum.auto()
    Arrow = enum.auto()

    Tilde = enum.auto()

    Equal = enum.auto()
    Bang = enum.auto()
    Plus = enum.auto()
    Minus = enum.auto()
    Star = enum.auto()
    Slash = enum.auto()
    Percent = enum.auto()
    Ampersand = enum.auto()
    Pipe = enum.auto()
    Caret = enum.auto()
    LShift = enum.auto()
    RShift = enum.auto()
    Greater = enum.auto()
    Lesser = enum.auto()

    EqualEqual = enum.auto()
    BangEqual = enum.auto()
    PlusEqual = enum.auto()
    MinusEqual = enum.auto()
    StarEqual = enum.auto()
    SlashEqual = enum.auto()
    PercentEqual = enum.auto()
    AmpersandEqual = enum.auto()
    PipeEqual = enum.auto()
    CaretEqual = enum.auto()
    LShiftEqual = enum.auto()
    RShiftEqual = enum.auto()
    GreaterEqual = enum.auto()
    LesserEqual = enum.auto()

    Identifier = enum.auto()
    BoolLiteral = enum.auto()
    IntLiteral = enum.auto()
    FloatLiteral = enum.auto()
    StringLiteral = enum.auto()

    AndKW = enum.auto()
    OrKW = enum.auto()
    NotKW = enum.auto()
    ReturnKW = enum.auto()
    IfKW = enum.auto()
    ElseKW = enum.auto()
    VarKW = enum.auto()
    FnKW = enum.auto()

    def __repr__(self):
        return str(self)[10:]


@dataclass
class UnknownCharacterError:
    char: str

    __slots__ = "char"

    def __repr__(self):
        return f"UnknownChar('{self.char}')"


@dataclass
class Token:
    type: TokenType
    value: typing.Any
    line: int

    __slots__ = "type", "value", "line"

    def __bool__(self) -> bool:
        return self.type > TokenType.EndOfFile


class Tokenizer:
    source: str
    idx: int
    line: int

    __slots__ = "source", "idx", "line"

    single_char_literals: dict[str, TokenType] = {
        "(": TokenType.LParen, ")": TokenType.RParen,
        "[": TokenType.LBracket, "]": TokenType.RBracket,
        "{": TokenType.LBrace, "}": TokenType.RBrace,
        ",": TokenType.Comma, ".": TokenType.Dot,
        ";": TokenType.Semicolon, ":": TokenType.Colon,
        "~": TokenType.Tilde
    }
    keyword_map: dict[str, TokenType] = {
        "and": TokenType.AndKW, "or": TokenType.OrKW,
        "not": TokenType.NotKW, "return": TokenType.ReturnKW,
        "if": TokenType.IfKW, "else": TokenType.ElseKW,
        "var": TokenType.VarKW, "fn": TokenType.FnKW
    }
    regular_operators: dict[str, tuple[TokenType, TokenType]] = {
        "+": (TokenType.Plus, TokenType.PlusEqual),
        "*": (TokenType.Star, TokenType.StarEqual),
        "/": (TokenType.Slash, TokenType.SlashEqual),
        "%": (TokenType.Percent, TokenType.PercentEqual),
        "&": (TokenType.Ampersand, TokenType.AmpersandEqual),
        "|": (TokenType.Pipe, TokenType.PipeEqual),
        "^": (TokenType.Caret, TokenType.CaretEqual),
        "!": (TokenType.Bang, TokenType.BangEqual),
        "=": (TokenType.Equal, TokenType.EqualEqual)
    }

    number_chars: str = "0123456789_"
    identifier_chars: str = ascii_letters + ascii_digits + "_"


    def __init__(self, text: str):
        self.source = text
        self.idx = 0
        self.line = 0

    def match(self, c: str) -> bool:
        if self.idx < len(self.source) and self.source[self.idx] == c:
            self.idx += 1
            return True
        else:
            return False


    def __call__(self) -> Token:
        while self.idx < len(self.source):
            c = self.source[self.idx]
            line = self.line
            self.idx += 1

            if c == ' ':
                continue
            elif c == '\n':
                self.line += 1
            elif c in self.single_char_literals:
                return Token(self.single_char_literals[c], None, line)
            elif c.isdigit():
                return self.tokenize_number()
            elif c.isalpha() or c == '_':
                return self.tokenize_identifier()
            elif c == '\'' or c == '"':
                return self.tokenize_string()

            if c in self.regular_operators:
                t: tuple[TokenType, TokenType] = self.regular_operators[c]
                if self.match('='):
                    return Token(t[1], None, self.line)
                else:
                    return Token(t[0], None, self.line)
            elif c == '-':
                if self.match(">"):
                    return Token(TokenType.Arrow, None, self.line)
                elif self.match("="):
                    return Token(TokenType.MinusEqual, None, self.line)
                else:
                    return Token(TokenType.Minus, None, self.line)
            elif c == '>':
                if self.match(">"):
                    if self.match("="):
                        return Token(TokenType.RShiftEqual, None, self.line)
                    else:
                        return Token(TokenType.RShift, None, self.line)
                elif self.match("="):
                    return Token(TokenType.GreaterEqual, None, self.line)
                else:
                    return Token(TokenType.Greater, None, self.line)

            elif c == '<':
                if self.match("<"):
                    if self.match("="):
                        return Token(TokenType.LShiftEqual, None, self.line)
                    else:
                        return Token(TokenType.LShift, None, self.line)
                elif self.match("="):
                    return Token(TokenType.LesserEqual, None, self.line)
                else:
                    return Token(TokenType.Lesser, None, self.line)

            else:
                return Token(TokenType.Error, UnknownCharacterError(c), self.line)

        return Token(TokenType.EndOfFile, self.idx, self.line)


    def tokenize_number(self) -> Token:
        start_idx: int = self.idx - 1
        while self.idx < len(self.source) and self.source[self.idx] in self.number_chars:
            self.idx += 1

        number: int = int(self.source[start_idx:self.idx])
        return Token(TokenType.IntLiteral, number, self.line)

    def tokenize_identifier(self) -> Token:
        start_idx: int = self.idx - 1
        while self.idx < len(self.source) and self.source[self.idx] in self.identifier_chars:
            self.idx += 1

        text: str = self.source[start_idx:self.idx]
        if text in self.keyword_map:
            return Token(self.keyword_map[text], None, self.line)
        else:
            return Token(TokenType.Identifier, sys.intern(text), self.line)

    def tokenize_string(self) -> Token:
        close: str = self.source[self.idx - 1]
        start_idx: int = self.idx
        start_line: int = self.line
        while self.idx < len(self.source) and self.source[self.idx] != close:
            if self.source[self.idx] == '\n':
                self.line += 1
            self.idx += 1
        self.idx += 1

        text: str = self.source[start_idx:self.idx - 1]
        return Token(TokenType.StringLiteral, text, start_line)


__all__ = (
    "TokenType", "Token", "Tokenizer", "UnknownCharacterError"
)