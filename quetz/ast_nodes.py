"""
Quetz Abstract Syntax Tree (AST) Node Classes
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from quetz.lexer import Token


class ASTNode:
    def __init__(self, line: int = 1, column: int = 1):
        self.line = line
        self.column = column


# ---------------------------------------------------------------------
# Expression Nodes
# ---------------------------------------------------------------------

class Expr(ASTNode):
    pass


class LiteralExpr(Expr):
    def __init__(self, value: Any, line: int, col: int):
        super().__init__(line, col)
        self.value = value


class IdentifierExpr(Expr):
    def __init__(self, name: str, line: int, col: int):
        super().__init__(line, col)
        self.name = name


class UnaryExpr(Expr):
    def __init__(self, op: Token, right: Expr, line: int, col: int):
        super().__init__(line, col)
        self.op = op
        self.right = right


class BinaryExpr(Expr):
    def __init__(self, left: Expr, op: Token, right: Expr, line: int, col: int):
        super().__init__(line, col)
        self.left = left
        self.op = op
        self.right = right


class AssignExpr(Expr):
    def __init__(self, name: str, value: Expr, op_token: Token, line: int, col: int):
        super().__init__(line, col)
        self.name = name
        self.value = value
        self.op_token = op_token


class IndexAssignExpr(Expr):
    def __init__(self, target: Expr, index: Expr, value: Expr, op_token: Token, line: int, col: int):
        super().__init__(line, col)
        self.target = target
        self.index = index
        self.value = value
        self.op_token = op_token


class CallExpr(Expr):
    def __init__(self, callee: Expr, args: List[Expr], line: int, col: int):
        super().__init__(line, col)
        self.callee = callee
        self.args = args


class IndexExpr(Expr):
    def __init__(self, target: Expr, index: Expr, line: int, col: int):
        super().__init__(line, col)
        self.target = target
        self.index = index


class ListExpr(Expr):
    def __init__(self, elements: List[Expr], line: int, col: int):
        super().__init__(line, col)
        self.elements = elements


class MapExpr(Expr):
    def __init__(self, pairs: List[Tuple[Expr, Expr]], line: int, col: int):
        super().__init__(line, col)
        self.pairs = pairs


@dataclass
class Param:
    name: str
    default: Optional[Expr] = None


class FunctionExpr(Expr):
    def __init__(self, name: Optional[str], params: List[Param], body: List[Stmt], line: int, col: int):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.body = body


# ---------------------------------------------------------------------
# Statement Nodes
# ---------------------------------------------------------------------

class Stmt(ASTNode):
    pass


class ExprStmt(Stmt):
    def __init__(self, expr: Expr, line: int, col: int):
        super().__init__(line, col)
        self.expr = expr


class LetStmt(Stmt):
    def __init__(self, name: str, initializer: Optional[Expr], line: int, col: int):
        super().__init__(line, col)
        self.name = name
        self.initializer = initializer


class BlockStmt(Stmt):
    def __init__(self, statements: List[Stmt], line: int, col: int):
        super().__init__(line, col)
        self.statements = statements


class IfStmt(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt], line: int, col: int):
        super().__init__(line, col)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt, line: int, col: int):
        super().__init__(line, col)
        self.condition = condition
        self.body = body


class ForInStmt(Stmt):
    def __init__(self, var_name: str, iterable: Expr, body: Stmt, line: int, col: int):
        super().__init__(line, col)
        self.var_name = var_name
        self.iterable = iterable
        self.body = body


class ReturnStmt(Stmt):
    def __init__(self, value: Optional[Expr], line: int, col: int):
        super().__init__(line, col)
        self.value = value


class BreakStmt(Stmt):
    pass


class ContinueStmt(Stmt):
    pass


class TryCatchStmt(Stmt):
    def __init__(self, try_block: Stmt, catch_var: Optional[str], catch_block: Stmt, line: int, col: int):
        super().__init__(line, col)
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block


class ThrowStmt(Stmt):
    def __init__(self, expr: Expr, line: int, col: int):
        super().__init__(line, col)
        self.expr = expr


class ImportStmt(Stmt):
    def __init__(self, path_expr: Expr, line: int, col: int):
        super().__init__(line, col)
        self.path_expr = path_expr
