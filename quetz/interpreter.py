"""
Quetz Tree-Walking Interpreter & Runtime Evaluator
"""

from __future__ import annotations
import os
from typing import Any, List, Optional

from quetz.lexer import TokenType, Token, Lexer
from quetz.parser import Parser
from quetz.environment import Environment
from quetz.callables import QuetzFunction, QuetzCallable
from quetz.builtins import init_builtins
from quetz.ast_nodes import (
    Expr, Stmt, LiteralExpr, IdentifierExpr, UnaryExpr, BinaryExpr,
    AssignExpr, IndexAssignExpr, CallExpr, IndexExpr, ListExpr, MapExpr,
    FunctionExpr, ExprStmt, LetStmt, BlockStmt, IfStmt, WhileStmt,
    ForInStmt, ReturnStmt, BreakStmt, ContinueStmt, TryCatchStmt,
    ThrowStmt, ImportStmt
)
from quetz.errors import (
    QuetzRuntimeError, ReturnException, BreakException, ContinueException,
    ThrowException
)


def is_truthy(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, (str, list, dict)):
        return len(val) > 0
    return True


def stringify(val: Any) -> str:
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return str(val)
    if isinstance(val, list):
        items = ", ".join(stringify(x) for x in val)
        return f"[{items}]"
    if isinstance(val, dict):
        pairs = ", ".join(f"{stringify(k)}: {stringify(v)}" for k, v in val.items())
        return f"{{{pairs}}}"
    return str(val)


class Interpreter:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.globals = Environment()
        self.environment = self.globals
        self.output_buffer: Optional[List[str]] = None
        self.current_source: Optional[str] = None
        init_builtins(self)

    def interpret(self, statements: List[Stmt], source: Optional[str] = None) -> Any:
        self.current_source = source
        result = None
        for stmt in statements:
            result = self.execute(stmt)
        return result

    def execute(self, stmt: Stmt) -> Any:
        if isinstance(stmt, ExprStmt):
            return self.evaluate(stmt.expr)
        elif isinstance(stmt, LetStmt):
            val = self.evaluate(stmt.initializer) if stmt.initializer is not None else None
            self.environment.define(stmt.name, val)
            return val
        elif isinstance(stmt, BlockStmt):
            return self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, IfStmt):
            cond = self.evaluate(stmt.condition)
            if is_truthy(cond):
                return self.execute(stmt.then_branch)
            elif stmt.else_branch is not None:
                return self.execute(stmt.else_branch)
            return None
        elif isinstance(stmt, WhileStmt):
            res = None
            while is_truthy(self.evaluate(stmt.condition)):
                try:
                    res = self.execute(stmt.body)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return res
        elif isinstance(stmt, ForInStmt):
            iterable = self.evaluate(stmt.iterable)
            res = None
            if isinstance(iterable, list):
                items = iterable
            elif isinstance(iterable, str):
                items = list(iterable)
            elif isinstance(iterable, dict):
                items = list(iterable.keys())
            else:
                raise QuetzRuntimeError(
                    f"Type '{type(iterable).__name__}' is not iterable.",
                    stmt.line, stmt.column, self.current_source
                )

            for item in items:
                loop_env = Environment(self.environment)
                loop_env.define(stmt.var_name, item)
                try:
                    res = self.execute_block(
                        stmt.body.statements if isinstance(stmt.body, BlockStmt) else [stmt.body],
                        loop_env
                    )
                except BreakException:
                    break
                except ContinueException:
                    continue
            return res
        elif isinstance(stmt, ReturnStmt):
            val = self.evaluate(stmt.value) if stmt.value is not None else None
            raise ReturnException(val)
        elif isinstance(stmt, BreakStmt):
            raise BreakException(stmt.line, stmt.column)
        elif isinstance(stmt, ContinueStmt):
            raise ContinueException(stmt.line, stmt.column)
        elif isinstance(stmt, ThrowStmt):
            val = self.evaluate(stmt.expr)
            raise ThrowException(val, stmt.line, stmt.column, self.current_source)
        elif isinstance(stmt, TryCatchStmt):
            try:
                return self.execute(stmt.try_block)
            except ThrowException as tex:
                catch_env = Environment(self.environment)
                if stmt.catch_var:
                    catch_env.define(stmt.catch_var, tex.value)
                return self.execute_block(
                    stmt.catch_block.statements if isinstance(stmt.catch_block, BlockStmt) else [stmt.catch_block],
                    catch_env
                )
            except QuetzRuntimeError as rex:
                catch_env = Environment(self.environment)
                if stmt.catch_var:
                    catch_env.define(stmt.catch_var, rex.message)
                return self.execute_block(
                    stmt.catch_block.statements if isinstance(stmt.catch_block, BlockStmt) else [stmt.catch_block],
                    catch_env
                )
        elif isinstance(stmt, ImportStmt):
            path_val = self.evaluate(stmt.path_expr)
            if not isinstance(path_val, str):
                raise QuetzRuntimeError("import statement requires a string file path.", stmt.line, stmt.column, self.current_source)
            full_path = os.path.join(self.base_dir, path_val) if not os.path.isabs(path_val) else path_val
            if not os.path.exists(full_path):
                raise QuetzRuntimeError(f"Module file '{path_val}' not found.", stmt.line, stmt.column, self.current_source)
            with open(full_path, "r", encoding="utf-8") as f:
                mod_src = f.read()
            tokens = Lexer(mod_src).tokenize()
            mod_stmts = Parser(tokens, mod_src).parse()
            prev_dir = self.base_dir
            prev_src = self.current_source
            self.base_dir = os.path.dirname(os.path.abspath(full_path))
            try:
                return self.interpret(mod_stmts, mod_src)
            finally:
                self.base_dir = prev_dir
                self.current_source = prev_src
        else:
            raise QuetzRuntimeError(f"Unknown statement: {type(stmt).__name__}", stmt.line, stmt.column, self.current_source)

    def execute_block(self, statements: List[Stmt], env: Environment) -> Any:
        prev_env = self.environment
        self.environment = env
        try:
            result = None
            for stmt in statements:
                result = self.execute(stmt)
            return result
        finally:
            self.environment = prev_env

    def evaluate(self, expr: Expr) -> Any:
        if isinstance(expr, LiteralExpr):
            return expr.value
        elif isinstance(expr, IdentifierExpr):
            return self.environment.get(expr.name, expr.line, expr.column, self.current_source)
        elif isinstance(expr, FunctionExpr):
            # Strategy: FunctionExpr creates and returns a QuetzFunction bound to the
            # lexical closure without self-defining in the environment. Named function declarations
            # are bound cleanly by the enclosing LetStmt produced by the parser.
            return QuetzFunction(expr, self.environment)
        elif isinstance(expr, ListExpr):
            return [self.evaluate(elem) for elem in expr.elements]
        elif isinstance(expr, MapExpr):
            d = {}
            for k_expr, v_expr in expr.pairs:
                k = self.evaluate(k_expr)
                v = self.evaluate(v_expr)
                if isinstance(k, (list, dict)):
                    raise QuetzRuntimeError("List and Map cannot be used as map keys.", expr.line, expr.column, self.current_source)
                d[k] = v
            return d
        elif isinstance(expr, UnaryExpr):
            right = self.evaluate(expr.right)
            if expr.op.type == TokenType.MINUS:
                if not isinstance(right, (int, float)):
                    raise QuetzRuntimeError("Operand must be a number.", expr.line, expr.column, self.current_source)
                return -right
            elif expr.op.type == TokenType.NOT:
                return not is_truthy(right)
            raise QuetzRuntimeError(f"Unknown unary operator: {expr.op.lexeme}", expr.line, expr.column, self.current_source)
        elif isinstance(expr, BinaryExpr):
            left = self.evaluate(expr.left)
            if expr.op.type == TokenType.AND:
                if not is_truthy(left):
                    return left
                return self.evaluate(expr.right)
            if expr.op.type == TokenType.OR:
                if is_truthy(left):
                    return left
                return self.evaluate(expr.right)

            right = self.evaluate(expr.right)

            if expr.op.type == TokenType.PLUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) or isinstance(right, str):
                    return stringify(left) + stringify(right)
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                raise QuetzRuntimeError(
                    f"Operator '+' not supported between {type(left).__name__} and {type(right).__name__}.",
                    expr.line, expr.column, self.current_source
                )
            if expr.op.type == TokenType.MINUS:
                self._check_number_operands(expr.op, left, right)
                return left - right
            if expr.op.type == TokenType.STAR:
                if isinstance(left, str) and isinstance(right, (int, float)):
                    return left * int(right)
                if isinstance(left, list) and isinstance(right, (int, float)):
                    return left * int(right)
                self._check_number_operands(expr.op, left, right)
                return left * right
            if expr.op.type == TokenType.SLASH:
                self._check_number_operands(expr.op, left, right)
                if right == 0:
                    raise QuetzRuntimeError("Division by zero.", expr.line, expr.column, self.current_source)
                return left / right
            if expr.op.type == TokenType.PERCENT:
                self._check_number_operands(expr.op, left, right)
                if right == 0:
                    raise QuetzRuntimeError("Modulo by zero.", expr.line, expr.column, self.current_source)
                return left % right
            if expr.op.type == TokenType.STAR_STAR:
                self._check_number_operands(expr.op, left, right)
                return left ** right
            if expr.op.type == TokenType.LT:
                return left < right
            if expr.op.type == TokenType.LTE:
                return left <= right
            if expr.op.type == TokenType.GT:
                return left > right
            if expr.op.type == TokenType.GTE:
                return left >= right
            if expr.op.type == TokenType.EQ:
                return left == right
            if expr.op.type == TokenType.NEQ:
                return left != right

            raise QuetzRuntimeError(f"Unsupported binary operator: {expr.op.lexeme}", expr.line, expr.column, self.current_source)

        elif isinstance(expr, AssignExpr):
            val = self.evaluate(expr.value)
            t = expr.op_token.type
            if t == TokenType.ASSIGN:
                target_val = val
            else:
                old = self.environment.get(expr.name, expr.line, expr.column, self.current_source)
                if t == TokenType.PLUS_ASSIGN:
                    if isinstance(old, (int, float)) and isinstance(val, (int, float)):
                        target_val = old + val
                    elif isinstance(old, str) or isinstance(val, str):
                        target_val = stringify(old) + stringify(val)
                    elif isinstance(old, list) and isinstance(val, list):
                        target_val = old + val
                    else:
                        raise QuetzRuntimeError(f"Invalid types for +=: {type(old).__name__} and {type(val).__name__}", expr.line, expr.column, self.current_source)
                elif t == TokenType.MINUS_ASSIGN:
                    self._check_number_operands(expr.op_token, old, val)
                    target_val = old - val
                elif t == TokenType.STAR_ASSIGN:
                    if isinstance(old, str) and isinstance(val, (int, float)):
                        target_val = old * int(val)
                    elif isinstance(old, list) and isinstance(val, (int, float)):
                        target_val = old * int(val)
                    else:
                        self._check_number_operands(expr.op_token, old, val)
                        target_val = old * val
                elif t == TokenType.SLASH_ASSIGN:
                    self._check_number_operands(expr.op_token, old, val)
                    if val == 0:
                        raise QuetzRuntimeError("Division by zero in /=.", expr.line, expr.column, self.current_source)
                    target_val = old / val
                elif t == TokenType.PERCENT_ASSIGN:
                    self._check_number_operands(expr.op_token, old, val)
                    if val == 0:
                        raise QuetzRuntimeError("Modulo by zero in %=.", expr.line, expr.column, self.current_source)
                    target_val = old % val
                else:
                    target_val = val

            self.environment.assign(expr.name, target_val, expr.line, expr.column, self.current_source)
            return target_val

        elif isinstance(expr, IndexAssignExpr):
            target = self.evaluate(expr.target)
            index = self.evaluate(expr.index)
            val = self.evaluate(expr.value)
            t = expr.op_token.type

            if isinstance(target, list):
                if not isinstance(index, (int, float)):
                    raise QuetzRuntimeError("List index must be a number.", expr.line, expr.column, self.current_source)
                idx = int(index)
                if idx < 0 or idx >= len(target):
                    raise QuetzRuntimeError(f"List index out of bounds: {idx}", expr.line, expr.column, self.current_source)

                if t == TokenType.ASSIGN:
                    target[idx] = val
                elif t == TokenType.PLUS_ASSIGN:
                    old = target[idx]
                    target[idx] = old + val if not (isinstance(old, str) or isinstance(val, str)) else stringify(old) + stringify(val)
                elif t == TokenType.MINUS_ASSIGN:
                    target[idx] = target[idx] - val
                elif t == TokenType.STAR_ASSIGN:
                    target[idx] = target[idx] * val
                elif t == TokenType.SLASH_ASSIGN:
                    if val == 0: raise QuetzRuntimeError("Division by zero in /=.", expr.line, expr.column, self.current_source)
                    target[idx] = target[idx] / val
                elif t == TokenType.PERCENT_ASSIGN:
                    if val == 0: raise QuetzRuntimeError("Modulo by zero in %=.", expr.line, expr.column, self.current_source)
                    target[idx] = target[idx] % val
                return target[idx]

            elif isinstance(target, dict):
                if t == TokenType.ASSIGN:
                    target[index] = val
                elif t == TokenType.PLUS_ASSIGN:
                    old = target.get(index, 0)
                    target[index] = old + val if not (isinstance(old, str) or isinstance(val, str)) else stringify(old) + stringify(val)
                elif t == TokenType.MINUS_ASSIGN:
                    target[index] = target.get(index, 0) - val
                elif t == TokenType.STAR_ASSIGN:
                    target[index] = target.get(index, 0) * val
                elif t == TokenType.SLASH_ASSIGN:
                    if val == 0: raise QuetzRuntimeError("Division by zero in /=.", expr.line, expr.column, self.current_source)
                    target[index] = target.get(index, 0) / val
                elif t == TokenType.PERCENT_ASSIGN:
                    if val == 0: raise QuetzRuntimeError("Modulo by zero in %=.", expr.line, expr.column, self.current_source)
                    target[index] = target.get(index, 0) % val
                return target[index]

            raise QuetzRuntimeError(f"Cannot index-assign into {type(target).__name__}.", expr.line, expr.column, self.current_source)

        elif isinstance(expr, IndexExpr):
            target = self.evaluate(expr.target)
            idx = self.evaluate(expr.index)

            if isinstance(target, list):
                if not isinstance(idx, (int, float)):
                    raise QuetzRuntimeError("List index must be a number.", expr.line, expr.column, self.current_source)
                i = int(idx)
                if i < 0 or i >= len(target):
                    raise QuetzRuntimeError(f"Index {i} out of bounds for list of length {len(target)}.", expr.line, expr.column, self.current_source)
                return target[i]
            elif isinstance(target, str):
                if not isinstance(idx, (int, float)):
                    raise QuetzRuntimeError("String index must be a number.", expr.line, expr.column, self.current_source)
                i = int(idx)
                if i < 0 or i >= len(target):
                    raise QuetzRuntimeError(f"Index {i} out of bounds for string of length {len(target)}.", expr.line, expr.column, self.current_source)
                return target[i]
            elif isinstance(target, dict):
                if idx not in target:
                    return None
                return target[idx]

            raise QuetzRuntimeError(f"Cannot index into {type(target).__name__}.", expr.line, expr.column, self.current_source)

        elif isinstance(expr, CallExpr):
            callee = self.evaluate(expr.callee)
            args = [self.evaluate(arg) for arg in expr.args]
            if not isinstance(callee, QuetzCallable):
                raise QuetzRuntimeError("Can only call functions.", expr.line, expr.column, self.current_source)
            return callee.call(self, args, expr.line, expr.column)

        raise QuetzRuntimeError(f"Unknown expression node: {type(expr).__name__}", expr.line, expr.column, self.current_source)

    def _check_number_operands(self, op: Token, left: Any, right: Any):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise QuetzRuntimeError("Operands must be numbers.", op.line, op.column, self.current_source)
