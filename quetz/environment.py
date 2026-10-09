"""
Quetz Lexical Scope Environment
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from quetz.errors import QuetzRuntimeError


class Environment:
    def __init__(self, enclosing: Optional[Environment] = None):
        self.values: Dict[str, Any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: str, line: int = 0, col: int = 0, source: Optional[str] = None) -> Any:
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name, line, col, source)
        raise QuetzRuntimeError(f"Undefined variable '{name}'.", line, col, source)

    def assign(self, name: str, value: Any, line: int = 0, col: int = 0, source: Optional[str] = None):
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value, line, col, source)
            return
        raise QuetzRuntimeError(f"Undefined variable '{name}' in assignment.", line, col, source)
