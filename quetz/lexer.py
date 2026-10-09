"""
Quetz Lexer and Token Definitions
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List

from quetz.errors import QuetzSyntaxError


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords
    LET = auto()
    FN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NIL = auto()
    BREAK = auto()
    CONTINUE = auto()
    IMPORT = auto()
    TRY = auto()
    CATCH = auto()
    THROW = auto()

    # Operators & Delimiters
    PLUS = auto()            # +
    MINUS = auto()           # -
    STAR = auto()            # *
    SLASH = auto()           # /
    PERCENT = auto()         # %
    STAR_STAR = auto()       # **

    ASSIGN = auto()          # =
    PLUS_ASSIGN = auto()     # +=
    MINUS_ASSIGN = auto()    # -=
    STAR_ASSIGN = auto()     # *=
    SLASH_ASSIGN = auto()    # /=
    PERCENT_ASSIGN = auto()  # %=

    EQ = auto()              # ==
    NEQ = auto()             # !=
    LT = auto()              # <
    LTE = auto()             # <=
    GT = auto()              # >
    GTE = auto()             # >=
    AND = auto()             # and
    OR = auto()              # or
    NOT = auto()             # not / !

    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACE = auto()          # {
    RBRACE = auto()          # }
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    COMMA = auto()           # ,
    COLON = auto()           # :
    SEMICOLON = auto()       # ;
    DOT = auto()             # .

    EOF = auto()


KEYWORDS = {
    "let": TokenType.LET,
    "fn": TokenType.FN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "import": TokenType.IMPORT,
    "try": TokenType.TRY,
    "catch": TokenType.CATCH,
    "throw": TokenType.THROW,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}


@dataclass
class Token:
    type: TokenType
    lexeme: str
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.lexeme!r}, line={self.line}, col={self.column})"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.token_start_col = 1

    def tokenize(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.token_start_col = self.column
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.column))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def add_token(self, type_: TokenType, value: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type_, text, value, self.line, self.token_start_col))

    def scan_token(self):
        c = self.advance()
        if c in " \r\t":
            return
        if c == "\n":
            self.line += 1
            self.column = 1
            return
        if c == "#":
            while self.peek() != "\n" and not self.is_at_end():
                self.advance()
            return

        if c == "(": self.add_token(TokenType.LPAREN); return
        if c == ")": self.add_token(TokenType.RPAREN); return
        if c == "{": self.add_token(TokenType.LBRACE); return
        if c == "}": self.add_token(TokenType.RBRACE); return
        if c == "[": self.add_token(TokenType.LBRACKET); return
        if c == "]": self.add_token(TokenType.RBRACKET); return
        if c == ",": self.add_token(TokenType.COMMA); return
        if c == ":": self.add_token(TokenType.COLON); return
        if c == ";": self.add_token(TokenType.SEMICOLON); return
        if c == ".": self.add_token(TokenType.DOT); return

        if c == "+":
            self.add_token(TokenType.PLUS_ASSIGN if self.match("=") else TokenType.PLUS)
            return
        if c == "-":
            self.add_token(TokenType.MINUS_ASSIGN if self.match("=") else TokenType.MINUS)
            return
        if c == "*":
            if self.match("*"):
                self.add_token(TokenType.STAR_STAR)
            elif self.match("="):
                self.add_token(TokenType.STAR_ASSIGN)
            else:
                self.add_token(TokenType.STAR)
            return
        if c == "/":
            self.add_token(TokenType.SLASH_ASSIGN if self.match("=") else TokenType.SLASH)
            return
        if c == "%":
            self.add_token(TokenType.PERCENT_ASSIGN if self.match("=") else TokenType.PERCENT)
            return
        if c == "=":
            self.add_token(TokenType.EQ if self.match("=") else TokenType.ASSIGN)
            return
        if c == "!":
            self.add_token(TokenType.NEQ if self.match("=") else TokenType.NOT)
            return
        if c == "<":
            self.add_token(TokenType.LTE if self.match("=") else TokenType.LT)
            return
        if c == ">":
            self.add_token(TokenType.GTE if self.match("=") else TokenType.GT)
            return

        if c == '"' or c == "'":
            self.string(c)
            return

        if c.isdigit():
            self.number()
            return

        if c.isalpha() or c == "_":
            self.identifier()
            return

        raise QuetzSyntaxError(f"Unexpected character: {c!r}", self.line, self.token_start_col, self.source)

    def string(self, quote: str):
        chars = []
        interp_depth = 0
        while not self.is_at_end():
            c = self.peek()
            if interp_depth > 0:
                if c == "\n":
                    self.line += 1
                    self.column = 1
                if c == "\\":
                    self.advance()
                    esc = self.advance()
                    chars.append("\\")
                    chars.append(esc)
                elif c == "{" and self.peek_next() != "":
                    chars.append(self.advance())
                elif c == "{":
                    interp_depth += 1
                    chars.append(self.advance())
                elif c == "}":
                    interp_depth -= 1
                    chars.append(self.advance())
                else:
                    chars.append(self.advance())
            else:
                if c == quote:
                    break
                if c == "\n":
                    self.line += 1
                    self.column = 1
                if c == "\\":
                    self.advance()
                    esc = self.advance()
                    if esc == "n": chars.append("\n")
                    elif esc == "t": chars.append("\t")
                    elif esc == "r": chars.append("\r")
                    elif esc == "\\": chars.append("\\")
                    elif esc == quote: chars.append(quote)
                    else: chars.append(esc)
                elif c == "$" and self.peek_next() == "{":
                    chars.append(self.advance())
                    chars.append(self.advance())
                    interp_depth += 1
                else:
                    chars.append(self.advance())

        if self.is_at_end():
            raise QuetzSyntaxError("Unterminated string literal.", self.line, self.token_start_col, self.source)

        self.advance()
        value = "".join(chars)
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        val_str = self.source[self.start:self.current]
        self.add_token(TokenType.NUMBER, float(val_str))

    def identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        text = self.source[self.start:self.current]
        type_ = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(type_, text)
