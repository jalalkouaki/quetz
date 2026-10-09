# Quetz Programming Language

[![Build Status](https://github.com/jalalkouaki/quetz/actions/workflows/test.yml/badge.svg)](https://github.com/jalalkouaki/quetz/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)

**Quetz** (`.qz`) is a clean, multi-paradigm, interpreted programming language built from scratch in Python 3.11+ with **zero external dependencies**. It provides an intuitive syntax, lexical closures, dynamic maps/lists, structured exceptions (`try`/`catch`/`throw`), and precise source-tracking error reporting.

---

## Architecture Overview

```
+--------------------+       +--------------------+       +--------------------+
|    Source Code     | ----> |    Quetz Lexer     | ----> |    Tokens with     |
|      (*.qz)        |       |  (Stream Scanner)  |       |  Line & Col Info   |
+--------------------+       +--------------------+       +--------------------+
                                                                     |
                                                                     v
+--------------------+       +--------------------+       +--------------------+
|   Value Output /   | <---- |    Tree-Walking    | <---- |     Recursive-     |
|    Side-Effects    |       |    Interpreter     |       |   Descent Parser   |
|    (CLI / REPL)    |       |   & Scoped Envs    |       |       (AST)        |
+--------------------+       +--------------------+       +--------------------+
```

---

## Features

- **Pure Python Standard Library**: Built solely using standard Python 3.11+ modules.
- **First-Class Functions & Lexical Closures**: Anonymous functions (`fn(x) { ... }`), default parameter values, and state encapsulation.
- **Dynamic Collections**: Heterogeneous lists (`[...]`) and hash maps (`{ ... }`) with indexing and compound update operators (`+=`, `-=`, `*=`, `/=`, `%=`).
- **Operators & Arithmetic**: Exponentiation (`**`), arithmetic, comparison, and short-circuit boolean logic (`and`, `or`, `not`).
- **String Interpolation**: Embedded expression evaluation via `"${expr}"`.
- **Control Flow**: `if`/`else if`/`else`, `while`, `for-in` over iterables (ranges, lists, maps), `break`, `continue`, `return`.
- **Exception Mechanism**: Structured `try { ... } catch (err) { ... }` with `throw`.
- **Diagnostic Errors**: Detailed error traces with 1-indexed line and column numbers and visual caret pointers.

---

## Installation & Quickstart

Clone the repository and run directly with Python 3.11+:

```bash
git clone https://github.com/jalalkouaki/quetz.git
cd quetz
python quetz.py --version
```

Or install as an editable CLI tool:
```bash
pip install -e .
quetz repl
```

---

## Usage

### Interactive REPL
```bash
python quetz.py repl
```

### Running Source Files
```bash
python quetz.py run examples/fibonacci.qz
python quetz.py run examples/functional.qz
```

### Syntax Verification (Parse-Only)
```bash
python quetz.py check examples/hello.qz
```

---

## Code Example

```quetz
# Higher-Order Functions & Maps in Quetz
fn make_counter(start = 0) {
    let count = start;
    return fn() {
        count += 1;
        return count;
    };
}

let counter = make_counter(0);
print(counter()); # 1
print(counter()); # 2

let user = { "name": "Quetz", "level": 1 };
user["level"] += 5;
print("User status: ${user["name"]} (Level ${user["level"]})");
```

---

## Development

Contributions and extensions are welcome! For architecture guidelines, coding conventions, and instructions on implementing new language features, please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

### Running Tests

Execute the full unit and integration test suite:

```bash
python -m unittest discover tests -v
```

---

## Roadmap

- [ ] Bytecode compilation and Virtual Machine (VM).
- [ ] Garbage collector inspection tooling.
- [ ] C Foreign Function Interface (FFI) support.
- [ ] Language Server Protocol (LSP) for VS Code.

---

## License

Distributed under the [MIT License](LICENSE). Copyright (c) 2026 Jalal Kouaki.
