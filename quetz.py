"""
Quetz Programming Language - Root Entry Point
"""

from quetz import Interpreter, run_source, check_source, VERSION
from quetz.errors import QuetzSyntaxError, QuetzRuntimeError
from quetz.cli import main, run_repl, run_file, check_file, print_help

if __name__ == "__main__":
    main()
