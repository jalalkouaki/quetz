"""
Quetz Error Types and Diagnostic Formatting
"""

from __future__ import annotations
from typing import Any, Optional


def format_error_with_source(error_type: str, message: str, line: int, col: int, source: Optional[str] = None) -> str:
    """
    Builds a diagnostic message with a source-line excerpt and caret pointing
    at the exact 1-based column of the offending character.
    """
    header = f"[{error_type} at Line {line}:{col}] {message}"
    if source is not None and line > 0:
        lines = source.splitlines()
        if 1 <= line <= len(lines):
            src_line = lines[line - 1]
            prefix = f"{line:4d} | "
            col_offset = max(0, col - 1)
            caret_line = " " * len(prefix) + " " * col_offset + "^"
            return f"{header}\n{prefix}{src_line}\n{caret_line}"
    return header


class QuetzSyntaxError(Exception):
    def __init__(self, message: str, line: int, column: int, source: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        super().__init__(format_error_with_source("SyntaxError", message, line, column, source))


class QuetzRuntimeError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0, source: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        super().__init__(format_error_with_source("RuntimeError", message, line, column, source))


class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value


class BreakException(Exception):
    def __init__(self, line: int = 0, col: int = 0):
        self.line = line
        self.col = col


class ContinueException(Exception):
    def __init__(self, line: int = 0, col: int = 0):
        self.line = line
        self.col = col


class ThrowException(Exception):
    def __init__(self, value: Any, line: int, col: int, source: Optional[str] = None):
        self.value = value
        self.line = line
        self.column = col
        self.source = source
