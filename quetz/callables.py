"""
Quetz Callables, User-Defined Functions, and Native Function Wrappers
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, List

from quetz.environment import Environment
from quetz.ast_nodes import FunctionExpr
from quetz.errors import (
    QuetzRuntimeError, ReturnException, BreakException, ContinueException,
    ThrowException
)

if TYPE_CHECKING:
    from quetz.interpreter import Interpreter


class QuetzCallable:
    def call(self, interpreter: Interpreter, args: List[Any], line: int, col: int) -> Any:
        raise NotImplementedError()


class QuetzFunction(QuetzCallable):
    def __init__(self, declaration: FunctionExpr, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: Interpreter, args: List[Any], line: int, col: int) -> Any:
        min_args = sum(1 for p in self.declaration.params if p.default is None)
        max_args = len(self.declaration.params)

        if len(args) < min_args or len(args) > max_args:
            fn_name = self.declaration.name or "<anonymous>"
            expected_str = f"{min_args}" if min_args == max_args else f"{min_args} to {max_args}"
            raise QuetzRuntimeError(
                f"Function '{fn_name}' expected {expected_str} arguments, got {len(args)}.",
                line, col, interpreter.current_source
            )

        env = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            if i < len(args):
                env.define(param.name, args[i])
            else:
                default_val = interpreter.evaluate(param.default) if param.default else None
                env.define(param.name, default_val)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as ret:
            return ret.value
        except (BreakException, ContinueException) as loop_jump:
            # Prevent break/continue from leaking outside function boundaries into caller loops
            err_line = loop_jump.line if loop_jump.line > 0 else line
            err_col = loop_jump.col if loop_jump.col > 0 else col
            raise QuetzRuntimeError(
                "Cannot use 'break' or 'continue' outside of a loop.",
                err_line, err_col, interpreter.current_source
            )
        return None

    def __repr__(self) -> str:
        name = self.declaration.name or "<anonymous>"
        return f"<fn {name}>"


class QuetzNativeFunction(QuetzCallable):
    def __init__(self, name: str, arity_count: int, fn: Callable[..., Any]):
        self.name = name
        self.arity_count = arity_count
        self.fn = fn

    def call(self, interpreter: Interpreter, args: List[Any], line: int, col: int) -> Any:
        if self.arity_count >= 0 and len(args) != self.arity_count:
            raise QuetzRuntimeError(
                f"Built-in function '{self.name}' expected {self.arity_count} arguments, got {len(args)}.",
                line, col, interpreter.current_source
            )
        try:
            return self.fn(interpreter, args, line, col)
        except (QuetzRuntimeError, ThrowException, ReturnException, BreakException, ContinueException):
            raise
        except Exception as err:
            raise QuetzRuntimeError(f"Error in '{self.name}': {err}", line, col, interpreter.current_source)

    def __repr__(self) -> str:
        return f"<native fn {self.name}>"
