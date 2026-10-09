# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Refactored interpreter into quetz/ package. Fixed caret alignment in diagnostics. Fixed break/continue leaking out of functions. Fixed double-definition of named functions.
- **Compound Assignment Operators**: Full support for `+=`, `-=`, `*=`, `/=`, and `%=` across variables, lists, and maps.
- **Exponentiation Operator**: Added right-associative `**` power operator.
- **String Interpolation**: Expressions can now be embedded directly within string literals via `"${expression}"`.
- **Default Parameter Values**: Function parameter lists now support default values (`fn name(param = default) { ... }`).
- **Functional Built-ins**: Added standard `map(list, fn)`, `filter(list, fn)`, and `reduce(list, fn, init)` functions.
- **Enhanced Error Diagnostics**: Source-line excerpts with column-aligned caret (`^`) pointers for syntax and runtime errors.
- **Syntax Check Mode**: Added `quetz check <file.qz>` CLI command for parse-only syntax verification.
- **CLI Flags**: Support for `--version`, `-v`, `--help`, and `-h` flags.
- **Examples**: Added `examples/strings.qz` and `examples/functional.qz`.
