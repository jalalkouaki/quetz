# Contributing to Quetz

Thank you for your interest in contributing to Quetz! This guide details how to set up your local development environment, run the test suite, implement new language features, and report issues.

---

## Development Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/jalalkouaki/quetz.git
   cd quetz
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv .venv

   # On Linux/macOS:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install Editable Package:**
   ```bash
   pip install -e .
   ```

---

## Running Tests and Examples

- **Run the full test suite:**
  ```bash
  python -m unittest discover tests -v
  ```

- **Run an example program:**
  ```bash
  python quetz.py run examples/hello.qz
  ```

- **Run the interactive REPL:**
  ```bash
  python quetz.py repl
  ```

- **Perform a parse-only syntax check:**
  ```bash
  python quetz.py check examples/hello.qz
  ```

---

## Adding a New Language Feature

When adding a language feature, follow this pipeline across the modular architecture:

1. **Lexer (`quetz/lexer.py`)**: Define token types in `TokenType` and add scanning logic in `Lexer.scan_token()` if introducing new syntax tokens or keywords.
2. **AST Node (`quetz/ast_nodes.py`)**: Define corresponding AST node classes subclassing `Expr` or `Stmt`.
3. **Parser (`quetz/parser.py`)**: Add recursive descent parsing rules in `Parser` with appropriate operator precedence.
4. **Interpreter (`quetz/interpreter.py` / `quetz/callables.py` / `quetz/builtins.py`)**: Implement runtime evaluation semantics in `Interpreter.execute()` or `Interpreter.evaluate()`.
5. **Unit Tests (`tests/test_quetz.py`)**: Write comprehensive unit tests for the AST and interpreter behavior.
6. **CLI Integration Tests (`tests/test_quetz_cli.py`)**: Write subprocess-based CLI integration tests validating end-to-end execution and error reporting.
7. **Example Programs (`examples/`)**: Add or update `.qz` example files showcasing the feature.
8. **Documentation (`docs/LANGUAGE.md` & `CHANGELOG.md`)**: Document the syntax, semantics, and update the changelog under `[Unreleased]`.

---

## Code Style & Guidelines

- **Zero Runtime Dependencies**: Quetz must remain implemented exclusively using the standard library (Python 3.11+).
- **PEP 8 Compliance**: Follow standard Python conventions with 4-space indentation.
- **Type Annotations**: Use type hints (`typing` / `from __future__ import annotations`) across functions and class methods.
- **Preserve Diagnostic Precision**: Errors must provide accurate 1-indexed line and column numbers.

---

## Reporting Bugs

To report a bug, open an issue on GitHub with:
1. Minimal reproducible `.qz` source code.
2. Expected output versus actual output (including error tracebacks).
3. Python version (`python --version`).
4. Operating system details.
