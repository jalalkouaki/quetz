"""
Unit test suite for Quetz interpreter.
Covers Lexer, Parser, Expressions, Control Flow, Closures, Built-ins,
Exceptions, Compound Assignments, Exponentiation, Interpolation,
Diagnostics Caret Alignment, and Function Boundary Scoping.
"""

import unittest
from quetz import Interpreter, run_source, check_source, VERSION
from quetz.errors import format_error_with_source


class TestQuetz(unittest.TestCase):
    def run_code(self, source: str):
        interp = Interpreter()
        interp.output_buffer = []
        res, err = run_source(source, interp=interp)
        return res, interp.output_buffer, err

    def test_arithmetic_and_precedence(self):
        res, _, err = self.run_code("let x = 2 + 3 * 4; return x;")
        self.assertIsNone(err)
        self.assertEqual(res, 14.0)

        res, _, err = self.run_code("return (10 - 4) / 2 + 2 * 1;")
        self.assertIsNone(err)
        self.assertEqual(res, 5.0)

    def test_exponentiation(self):
        res, _, err = self.run_code("return 2 ** 3;")
        self.assertIsNone(err)
        self.assertEqual(res, 8.0)

        # Right-associative: 2 ** (3 ** 2) = 2 ** 9 = 512
        res, _, err = self.run_code("return 2 ** 3 ** 2;")
        self.assertIsNone(err)
        self.assertEqual(res, 512.0)

    def test_compound_assignments(self):
        code = """
        let a = 10;
        a += 5;
        a -= 3;
        a *= 2;
        a /= 4;
        a %= 5;
        return a;
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, 1.0)

    def test_string_interpolation(self):
        code = """
        let name = "Quetz";
        let year = 2026;
        let s = "Language: ${name}, Year: ${year + 1}";
        return s;
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, "Language: Quetz, Year: 2027")

    def test_else_if_chaining(self):
        code = """
        fn classify(score) {
            if score >= 90 {
                return "A";
            } else if score >= 80 {
                return "B";
            } else if score >= 70 {
                return "C";
            } else {
                return "F";
            }
        }
        return [classify(95), classify(82), classify(74), classify(50)];
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, ["A", "B", "C", "F"])

    def test_default_parameters(self):
        code = """
        fn greet(name = "world", prefix = "Hello") {
            return "${prefix}, ${name}!";
        }
        return [greet(), greet("Alice"), greet("Bob", "Hi")];
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, ["Hello, world!", "Hello, Alice!", "Hi, Bob!"])

    def test_functional_builtins(self):
        code = """
        let nums = [1, 2, 3, 4];
        let squared = map(nums, fn(x) { return x ** 2; });
        let evens = filter(squared, fn(x) { return x % 2 == 0; });
        let sum = reduce(evens, fn(acc, x) { return acc + x; }, 0);
        return sum;
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, 20.0)

    def test_strings_and_concatenation(self):
        res, out, err = self.run_code('let s = "Hello, " + "World!"; print(s); return s;')
        self.assertIsNone(err)
        self.assertEqual(res, "Hello, World!")
        self.assertEqual(out, ["Hello, World!"])

    def test_control_flow(self):
        code = """
        let sum = 0;
        let i = 1;
        while i <= 5 {
            sum += i;
            i += 1;
        }
        return sum;
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, 15.0)

    def test_for_in_and_range(self):
        code = """
        let total = 0;
        for x in range(1, 6) {
            total += x;
        }
        return total;
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, 15.0)

    def test_closures_and_first_class_functions(self):
        code = """
        fn make_adder(n) {
            return fn(x) {
                return x + n;
            };
        }
        let add5 = make_adder(5);
        return add5(10);
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, 15.0)

    def test_named_recursive_function(self):
        code = """
        fn factorial(n) {
            if n <= 1 {
                return 1;
            }
            return n * factorial(n - 1);
        }
        return factorial(5);
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, 120.0)

    def test_break_and_continue_isolated_to_function_boundary(self):
        # Break inside a function called from a loop must raise a runtime error
        code = """
        fn bad_break() {
            break;
        }
        let iterations = 0;
        let caught_err = "";
        while iterations < 3 {
            iterations += 1;
            try {
                bad_break();
            } catch (e) {
                caught_err = e;
                break;
            }
        }
        return [iterations, caught_err];
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res[0], 1.0)
        self.assertIn("Cannot use 'break' or 'continue' outside of a loop", res[1])

    def test_lists_and_maps(self):
        code = """
        let lst = [1, 2];
        push(lst, 3);
        let m = { "a": 10, "b": 20 };
        m["c"] = 30;
        return len(lst) + m["c"];
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, 33.0)

    def test_exception_handling(self):
        code = """
        let caught = "none";
        try {
            throw "custom error";
        } catch (e) {
            caught = e;
        }
        return caught;
        """
        res, _, err = self.run_code(code)
        self.assertIsNone(err)
        self.assertEqual(res, "custom error")

    def test_caret_alignment_accuracy(self):
        source = "fn broken( {"
        err = check_source(source)
        self.assertIsNotNone(err)
        lines = err.splitlines()
        self.assertEqual(len(lines), 3)

        source_line = lines[1]
        caret_line = lines[2]

        caret_index = caret_line.index("^")
        # In 'fn broken( {', token '{' is at 1-based column 12
        # In lines[1] ('   1 | fn broken( {'), character at caret_index must be '{'
        self.assertEqual(source_line[caret_index], "{")

    def test_diagnostics_formatting_with_multiline_and_width(self):
        source = "let a = 10;\nlet b = 20;\nlet c = a + undefined_var;"
        _, _, err = self.run_code(source)
        self.assertIsNotNone(err)
        self.assertIn("Line 3", err)
        self.assertIn("^", err)


if __name__ == "__main__":
    unittest.main()
