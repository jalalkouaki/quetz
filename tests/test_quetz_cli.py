"""
Subprocess-based CLI and end-to-end integration test suite for Quetz.
"""

from __future__ import annotations
import os
import sys
import tempfile
import unittest
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY_POINT = os.path.join(REPO_ROOT, "quetz.py")


class TestQuetzCLI(unittest.TestCase):
    def run_cli(self, *args: str, input_str: str | None = None, timeout: int = 15) -> subprocess.CompletedProcess:
        cmd = [sys.executable, ENTRY_POINT] + list(args)
        return subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            input=input_str,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def test_version_subcommand(self):
        res = self.run_cli("version")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Quetz v", res.stdout)

    def test_version_flags(self):
        res_long = self.run_cli("--version")
        self.assertEqual(res_long.returncode, 0)
        self.assertIn("Quetz v", res_long.stdout)

        res_short = self.run_cli("-v")
        self.assertEqual(res_short.returncode, 0)
        self.assertIn("Quetz v", res_short.stdout)

    def test_help_flag(self):
        res = self.run_cli("--help")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Usage:", res.stdout)
        self.assertIn("quetz run", res.stdout)
        self.assertIn("quetz check", res.stdout)

    def test_run_hello_example(self):
        example_path = os.path.join(REPO_ROOT, "examples", "hello.qz")
        res = self.run_cli("run", example_path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Hello, World from Quetz!", res.stdout)
        self.assertIn("Ada Lovelace", res.stdout)

    def test_run_fibonacci_example(self):
        example_path = os.path.join(REPO_ROOT, "examples", "fibonacci.qz")
        res = self.run_cli("run", example_path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("fib(9) = 34", res.stdout)

    def test_run_strings_example(self):
        example_path = os.path.join(REPO_ROOT, "examples", "strings.qz")
        res = self.run_cli("run", example_path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Quetz is expressive!", res.stdout)

    def test_run_functional_example(self):
        example_path = os.path.join(REPO_ROOT, "examples", "functional.qz")
        res = self.run_cli("run", example_path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Final val after compound operations: 5", res.stdout)

    def test_check_valid_file(self):
        example_path = os.path.join(REPO_ROOT, "examples", "hello.qz")
        res = self.run_cli("check", example_path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("OK:", res.stdout)
        self.assertIn("passed syntax check", res.stdout)

    def test_check_invalid_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qz", delete=False) as f:
            f.write("fn broken( {")
            temp_path = f.name

        try:
            res = self.run_cli("check", temp_path)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("SyntaxError", res.stderr)
            self.assertIn("^", res.stderr)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_missing_file(self):
        res = self.run_cli("run", "non_existent_file.qz")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("does not exist", res.stderr)

    def test_arithmetic_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qz", delete=False) as f:
            f.write("print(2 + 3 * 4);\n")
            temp_path = f.name

        try:
            res = self.run_cli("run", temp_path)
            self.assertEqual(res.returncode, 0)
            self.assertEqual(res.stdout.strip(), "14")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_string_interpolation(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qz", delete=False) as f:
            f.write('let a = 1; let b = 1; print("Answer is ${a + b}");\n')
            temp_path = f.name

        try:
            res = self.run_cli("run", temp_path)
            self.assertEqual(res.returncode, 0)
            self.assertEqual(res.stdout.strip(), "Answer is 2")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_closure_via_cli(self):
        code = """
        fn make_adder(n) {
            return fn(x) { return x + n; };
        }
        let add10 = make_adder(10);
        print(add10(32));
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qz", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            res = self.run_cli("run", temp_path)
            self.assertEqual(res.returncode, 0)
            self.assertEqual(res.stdout.strip(), "42")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_break_outside_function_loop_error(self):
        code = """
        fn jump() {
            break;
        }
        while true {
            jump();
        }
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qz", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            res = self.run_cli("run", temp_path)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("Cannot use 'break' or 'continue' outside of a loop", res.stderr)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_undefined_variable_error(self):
        code = "let x = 10;\nlet y = x + missing_var;\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qz", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            res = self.run_cli("run", temp_path)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("Undefined variable 'missing_var'", res.stderr)
            self.assertIn("Line 2", res.stderr)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_repl_smoke(self):
        repl_input = "let x = 5\nx * 2\nexit\n"
        res = self.run_cli("repl", input_str=repl_input)
        self.assertEqual(res.returncode, 0)
        self.assertIn("10", res.stdout)

    def test_module_execution_via_python_m(self):
        example_path = os.path.join(REPO_ROOT, "examples", "hello.qz")
        cmd = [sys.executable, "-m", "quetz", "run", example_path]
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Hello, World from Quetz!", res.stdout)


if __name__ == "__main__":
    unittest.main()
