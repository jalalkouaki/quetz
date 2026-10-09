"""
Quetz Programming Language Package
"""

from quetz.interpreter import Interpreter
from quetz.cli import run_source, check_source

VERSION = "0.2.0"

__all__ = [
    "Interpreter",
    "run_source",
    "check_source",
    "VERSION"
]
