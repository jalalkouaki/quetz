"""
Quetz Command-Line Interface and REPL Driver
"""

from __future__ import annotations
import sys
import os
from typing import Any, Optional, Tuple

from quetz.lexer import Lexer, TokenType
from quetz.parser import Parser
from quetz.interpreter import Interpreter, stringify
from quetz.errors import (
    QuetzSyntaxError, QuetzRuntimeError, ThrowException, ReturnException,
    BreakException, ContinueException, format_error_with_source
)


def get_version() -> str:
    from quetz import VERSION
    return VERSION


def run_source(source: str, interp: Optional[Interpreter] = None, base_dir: str = ".") -> Tuple[Any, Optional[str]]:
    if interp is None:
        interp = Interpreter(base_dir=base_dir)
    try:
        tokens = Lexer(source).tokenize()
        statements = Parser(tokens, source).parse()
        res = interp.interpret(statements, source)
        return res, None
    except ReturnException as e:
        return e.value, None
    except (BreakException, ContinueException) as e:
        err = format_error_with_source("RuntimeError", "Cannot use 'break' or 'continue' outside of a loop.", e.line, e.col, source)
        return None, err
    except (QuetzSyntaxError, QuetzRuntimeError) as e:
        return None, str(e)
    except ThrowException as e:
        formatted = format_error_with_source("Uncaught Throw", stringify(e.value), e.line, e.column, e.source)
        return None, formatted
    except Exception as e:
        return None, f"Internal Error: {e}"


def check_source(source: str) -> Optional[str]:
    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens, source).parse()
        return None
    except (QuetzSyntaxError, QuetzRuntimeError) as e:
        return str(e)
    except Exception as e:
        return f"Syntax check failed: {e}"


def run_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(file_path))
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    interp = Interpreter(base_dir=base_dir)
    _, err = run_source(source, interp=interp, base_dir=base_dir)
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)


def check_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    err = check_source(source)
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)
    else:
        print(f"OK: '{file_path}' passed syntax check.")


def run_repl():
    version = get_version()
    print(f"Quetz Programming Language v{version} (Interactive REPL)")
    print("Type 'exit' or press Ctrl+C/Ctrl+D to exit.\n")

    interp = Interpreter(base_dir=".")
    while True:
        try:
            line = input("quetz> ")
            if line.strip() in ("exit", "quit"):
                break
            if not line.strip():
                continue

            while line.count("{") > line.count("}") or line.count("(") > line.count(")"):
                more = input("...    ")
                line += "\n" + more

            tokens = Lexer(line).tokenize()
            try:
                expr_parser = Parser(tokens, line)
                expr = expr_parser.expression()
                if expr_parser.is_at_end() or expr_parser.check(TokenType.SEMICOLON):
                    interp.current_source = line
                    val = interp.evaluate(expr)
                    if val is not None:
                        print(stringify(val))
                    continue
            except Exception:
                pass

            stmts = Parser(tokens, line).parse()
            res = interp.interpret(stmts, line)
            if res is not None:
                print(stringify(res))

        except (QuetzSyntaxError, QuetzRuntimeError) as e:
            print(e, file=sys.stderr)
        except ThrowException as e:
            print(format_error_with_source("Uncaught Throw", stringify(e.value), e.line, e.column, line), file=sys.stderr)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


def print_help():
    version = get_version()
    print(f"Quetz Programming Language v{version}")
    print("\nUsage:")
    print("  quetz repl              Start interactive REPL")
    print("  quetz run <file.qz>     Execute a Quetz source script")
    print("  quetz check <file.qz>   Parse-only syntax check")
    print("  quetz version           Show version information")
    print("\nFlags:")
    print("  -v, --version           Show version information")
    print("  -h, --help              Show this help message")


def main():
    args = sys.argv[1:]
    if not args:
        run_repl()
        return

    cmd = args[0]
    if cmd == "repl":
        run_repl()
    elif cmd == "run":
        if len(args) < 2:
            print("Usage: quetz run <file.qz>", file=sys.stderr)
            sys.exit(1)
        run_file(args[1])
    elif cmd == "check":
        if len(args) < 2:
            print("Usage: quetz check <file.qz>", file=sys.stderr)
            sys.exit(1)
        check_file(args[1])
    elif cmd in ("version", "--version", "-v"):
        print(f"Quetz v{get_version()}")
    elif cmd in ("help", "--help", "-h"):
        print_help()
    else:
        if cmd.endswith(".qz"):
            run_file(cmd)
        else:
            print(f"Unknown command or flag: '{cmd}'. Use 'quetz --help'.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
