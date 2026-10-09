"""
Quetz Recursive Descent Pratt Parser
"""

from __future__ import annotations
from typing import List, Optional

from quetz.lexer import Token, TokenType, Lexer
from quetz.errors import QuetzSyntaxError
from quetz.ast_nodes import (
    Expr, Stmt, LiteralExpr, IdentifierExpr, UnaryExpr, BinaryExpr,
    AssignExpr, IndexAssignExpr, CallExpr, IndexExpr, ListExpr, MapExpr,
    FunctionExpr, Param, ExprStmt, LetStmt, BlockStmt, IfStmt, WhileStmt,
    ForInStmt, ReturnStmt, BreakStmt, ContinueStmt, TryCatchStmt,
    ThrowStmt, ImportStmt
)


class Parser:
    def __init__(self, tokens: List[Token], source: Optional[str] = None):
        self.tokens = tokens
        self.source = source
        self.current = 0

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self.is_at_end():
            if self.match(TokenType.SEMICOLON):
                continue
            statements.append(self.declaration())
        return statements

    # --- Navigation Helpers ---

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, type_: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        token = self.peek()
        raise QuetzSyntaxError(message, token.line, token.column, self.source)

    # --- Statement Parsers ---

    def declaration(self) -> Stmt:
        try:
            if self.match(TokenType.LET):
                return self.let_declaration()
            if self.check(TokenType.FN) and self.peek_next_is_identifier():
                self.advance()
                return self.function_declaration()
            return self.statement()
        except QuetzSyntaxError:
            self.synchronize()
            raise

    def peek_next_is_identifier(self) -> bool:
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1].type == TokenType.IDENTIFIER
        return False

    def let_declaration(self) -> Stmt:
        tok = self.previous()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expect variable name after 'let'.")
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        self.match(TokenType.SEMICOLON)
        return LetStmt(name_tok.lexeme, initializer, tok.line, tok.column)

    def parse_parameter_list(self) -> List[Param]:
        params: List[Param] = []
        if not self.check(TokenType.RPAREN):
            while True:
                p = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                default_expr = None
                if self.match(TokenType.ASSIGN):
                    default_expr = self.expression()
                params.append(Param(p.lexeme, default_expr))
                if not self.match(TokenType.COMMA):
                    break
        return params

    def function_declaration(self) -> Stmt:
        tok = self.previous()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        params = self.parse_parameter_list()
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LBRACE, "Expect '{' before function body.")
        body = self.block_statements()
        fn_expr = FunctionExpr(name_tok.lexeme, params, body, tok.line, tok.column)
        return LetStmt(name_tok.lexeme, fn_expr, tok.line, tok.column)

    def statement(self) -> Stmt:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.BREAK):
            tok = self.previous()
            self.match(TokenType.SEMICOLON)
            return BreakStmt(tok.line, tok.column)
        if self.match(TokenType.CONTINUE):
            tok = self.previous()
            self.match(TokenType.SEMICOLON)
            return ContinueStmt(tok.line, tok.column)
        if self.match(TokenType.TRY):
            return self.try_statement()
        if self.match(TokenType.THROW):
            return self.throw_statement()
        if self.match(TokenType.IMPORT):
            return self.import_statement()
        if self.match(TokenType.LBRACE):
            tok = self.previous()
            return BlockStmt(self.block_statements(), tok.line, tok.column)
        return self.expression_statement()

    def if_statement(self) -> Stmt:
        tok = self.previous()
        cond = self.expression()
        self.consume(TokenType.LBRACE, "Expect '{' after if condition.")
        then_branch = BlockStmt(self.block_statements(), tok.line, tok.column)
        else_branch = None
        if self.match(TokenType.ELSE):
            if self.match(TokenType.IF):
                else_branch = self.if_statement()
            else:
                self.consume(TokenType.LBRACE, "Expect '{' after 'else'.")
                else_branch = BlockStmt(self.block_statements(), tok.line, tok.column)
        return IfStmt(cond, then_branch, else_branch, tok.line, tok.column)

    def while_statement(self) -> Stmt:
        tok = self.previous()
        cond = self.expression()
        self.consume(TokenType.LBRACE, "Expect '{' after while condition.")
        body = BlockStmt(self.block_statements(), tok.line, tok.column)
        return WhileStmt(cond, body, tok.line, tok.column)

    def for_statement(self) -> Stmt:
        tok = self.previous()
        var_tok = self.consume(TokenType.IDENTIFIER, "Expect loop variable name after 'for'.")
        self.consume(TokenType.IN, "Expect 'in' after loop variable.")
        iterable = self.expression()
        self.consume(TokenType.LBRACE, "Expect '{' before loop body.")
        body = BlockStmt(self.block_statements(), tok.line, tok.column)
        return ForInStmt(var_tok.lexeme, iterable, body, tok.line, tok.column)

    def return_statement(self) -> Stmt:
        tok = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON) and not self.check(TokenType.RBRACE) and not self.is_at_end():
            value = self.expression()
        self.match(TokenType.SEMICOLON)
        return ReturnStmt(value, tok.line, tok.column)

    def try_statement(self) -> Stmt:
        tok = self.previous()
        self.consume(TokenType.LBRACE, "Expect '{' after 'try'.")
        try_block = BlockStmt(self.block_statements(), tok.line, tok.column)
        self.consume(TokenType.CATCH, "Expect 'catch' block after 'try'.")
        catch_var = None
        if self.match(TokenType.LPAREN):
            v = self.consume(TokenType.IDENTIFIER, "Expect catch error variable name.")
            catch_var = v.lexeme
            self.consume(TokenType.RPAREN, "Expect ')' after catch parameter.")
        elif self.check(TokenType.IDENTIFIER):
            catch_var = self.advance().lexeme
        self.consume(TokenType.LBRACE, "Expect '{' before catch body.")
        catch_block = BlockStmt(self.block_statements(), tok.line, tok.column)
        return TryCatchStmt(try_block, catch_var, catch_block, tok.line, tok.column)

    def throw_statement(self) -> Stmt:
        tok = self.previous()
        expr = self.expression()
        self.match(TokenType.SEMICOLON)
        return ThrowStmt(expr, tok.line, tok.column)

    def import_statement(self) -> Stmt:
        tok = self.previous()
        path_expr = self.expression()
        self.match(TokenType.SEMICOLON)
        return ImportStmt(path_expr, tok.line, tok.column)

    def block_statements(self) -> List[Stmt]:
        stmts: List[Stmt] = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            if self.match(TokenType.SEMICOLON):
                continue
            stmts.append(self.declaration())
        self.consume(TokenType.RBRACE, "Expect '}' after block.")
        return stmts

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.match(TokenType.SEMICOLON)
        return ExprStmt(expr, expr.line, expr.column)

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in (
                TokenType.LET, TokenType.FN, TokenType.IF, TokenType.WHILE,
                TokenType.FOR, TokenType.RETURN, TokenType.TRY, TokenType.THROW,
                TokenType.IMPORT, TokenType.RBRACE
            ):
                return
            self.advance()

    # --- Expression Parsers ---

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.logic_or()

        assign_ops = (
            TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
            TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN, TokenType.PERCENT_ASSIGN
        )
        if self.match(*assign_ops):
            op = self.previous()
            value = self.assignment()

            if isinstance(expr, IdentifierExpr):
                return AssignExpr(expr.name, value, op, expr.line, expr.column)
            elif isinstance(expr, IndexExpr):
                return IndexAssignExpr(expr.target, expr.index, value, op, expr.line, expr.column)

            raise QuetzSyntaxError("Invalid assignment target.", op.line, op.column, self.source)

        return expr

    def logic_or(self) -> Expr:
        expr = self.logic_and()
        while self.match(TokenType.OR):
            op = self.previous()
            right = self.logic_and()
            expr = BinaryExpr(expr, op, right, op.line, op.column)
        return expr

    def logic_and(self) -> Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous()
            right = self.equality()
            expr = BinaryExpr(expr, op, right, op.line, op.column)
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TokenType.EQ, TokenType.NEQ):
            op = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, op, right, op.line, op.column)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self.match(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op = self.previous()
            right = self.term()
            expr = BinaryExpr(expr, op, right, op.line, op.column)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, op, right, op.line, op.column)
        return expr

    def factor(self) -> Expr:
        expr = self.power()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.previous()
            right = self.power()
            expr = BinaryExpr(expr, op, right, op.line, op.column)
        return expr

    def power(self) -> Expr:
        expr = self.unary()
        if self.match(TokenType.STAR_STAR):
            op = self.previous()
            right = self.power()
            return BinaryExpr(expr, op, right, op.line, op.column)
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.previous()
            right = self.unary()
            return UnaryExpr(op, right, op.line, op.column)
        return self.call_or_index()

    def call_or_index(self) -> Expr:
        expr = self.primary()

        while True:
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.expression())
                        if not self.match(TokenType.COMMA):
                            break
                tok = self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
                expr = CallExpr(expr, args, tok.line, tok.column)
            elif self.match(TokenType.LBRACKET):
                index = self.expression()
                tok = self.consume(TokenType.RBRACKET, "Expect ']' after index.")
                expr = IndexExpr(expr, index, tok.line, tok.column)
            else:
                break

        return expr

    def parse_interpolated_string(self, raw: str, line: int, col: int) -> Expr:
        if "${" not in raw:
            return LiteralExpr(raw, line, col)

        parts: List[Expr] = []
        i = 0
        n = len(raw)
        buf = []

        while i < n:
            if raw[i:i+2] == "${":
                if buf:
                    parts.append(LiteralExpr("".join(buf), line, col))
                    buf = []
                i += 2
                depth = 1
                expr_chars = []
                in_quote = None
                while i < n and depth > 0:
                    ch = raw[i]
                    if in_quote:
                        if ch == "\\":
                            expr_chars.append(ch)
                            i += 1
                            if i < n:
                                expr_chars.append(raw[i])
                                i += 1
                            continue
                        elif ch == in_quote:
                            in_quote = None
                    else:
                        if ch in ('"', "'"):
                            in_quote = ch
                        elif ch == "{":
                            depth += 1
                        elif ch == "}":
                            depth -= 1
                            if depth == 0:
                                i += 1
                                break
                    expr_chars.append(ch)
                    i += 1

                expr_src = "".join(expr_chars).strip()
                if not expr_src:
                    parts.append(LiteralExpr("", line, col))
                else:
                    sub_toks = Lexer(expr_src).tokenize()
                    sub_ast = Parser(sub_toks, self.source).expression()
                    parts.append(CallExpr(IdentifierExpr("str", line, col), [sub_ast], line, col))
            else:
                buf.append(raw[i])
                i += 1

        if buf:
            parts.append(LiteralExpr("".join(buf), line, col))

        if not parts:
            return LiteralExpr("", line, col)
        if len(parts) == 1:
            return parts[0]

        res = parts[0]
        plus_tok = Token(TokenType.PLUS, "+", None, line, col)
        for p in parts[1:]:
            res = BinaryExpr(res, plus_tok, p, line, col)
        return res

    def primary(self) -> Expr:
        tok = self.peek()

        if self.match(TokenType.TRUE):
            return LiteralExpr(True, tok.line, tok.column)
        if self.match(TokenType.FALSE):
            return LiteralExpr(False, tok.line, tok.column)
        if self.match(TokenType.NIL):
            return LiteralExpr(None, tok.line, tok.column)
        if self.match(TokenType.NUMBER):
            return LiteralExpr(self.previous().value, tok.line, tok.column)
        if self.match(TokenType.STRING):
            return self.parse_interpolated_string(self.previous().value, tok.line, tok.column)

        if self.match(TokenType.IDENTIFIER):
            return IdentifierExpr(self.previous().lexeme, tok.line, tok.column)

        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return expr

        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.expression())
                    if not self.match(TokenType.COMMA):
                        break
            self.consume(TokenType.RBRACKET, "Expect ']' after list elements.")
            return ListExpr(elements, tok.line, tok.column)

        if self.match(TokenType.LBRACE):
            pairs = []
            if not self.check(TokenType.RBRACE):
                while True:
                    key = self.expression()
                    self.consume(TokenType.COLON, "Expect ':' after map key.")
                    val = self.expression()
                    pairs.append((key, val))
                    if not self.match(TokenType.COMMA):
                        break
            self.consume(TokenType.RBRACE, "Expect '}' after map entries.")
            return MapExpr(pairs, tok.line, tok.column)

        if self.match(TokenType.FN):
            self.consume(TokenType.LPAREN, "Expect '(' after 'fn'.")
            params = self.parse_parameter_list()
            self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
            self.consume(TokenType.LBRACE, "Expect '{' before function body.")
            body = self.block_statements()
            return FunctionExpr(None, params, body, tok.line, tok.column)

        raise QuetzSyntaxError(f"Unexpected token: {tok.lexeme!r}", tok.line, tok.column, self.source)
