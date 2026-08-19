"""
Unit Tests for Pleximus AI Agent Calculator Tool
=================================================
Automated test suite verifying functional requirements, edge cases,
error handling, and security protections.
"""

import math
import unittest
from calculator import calculator, evaluate_expression


class TestCalculatorBasicArithmetic(unittest.TestCase):
    """Test FR-1: Basic Arithmetic Operations."""

    def test_addition(self):
        res = calculator("10 + 20")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 30)

    def test_subtraction(self):
        res = calculator("100 - 25")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 75)

    def test_multiplication(self):
        res = calculator("5 * 8")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 40)

        res2 = calculator("25 * 4")
        self.assertTrue(res2["success"])
        self.assertEqual(res2["result"], 100)

    def test_division(self):
        res = calculator("100 / 4")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 25)

        res2 = calculator("100 / 5")
        self.assertTrue(res2["success"])
        self.assertEqual(res2["result"], 20)

    def test_modulus(self):
        res = calculator("10 % 3")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 1)

    def test_exponentiation(self):
        res = calculator("2 ** 5")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 32)

    def test_floor_division(self):
        res = calculator("17 // 5")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 3)


class TestCalculatorPrecedenceAndParentheses(unittest.TestCase):
    """Test FR-2: Parentheses and Mathematical Precedence."""

    def test_parentheses_multiplication(self):
        res = calculator("(10 + 20) * 2")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 60)

    def test_parentheses_division(self):
        res = calculator("100 / (5 + 5)")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 10)

    def test_nested_parentheses(self):
        res = calculator("2 * (3 + (4 * 2))")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 22)

    def test_standard_precedence(self):
        # Multiplication before addition
        res = calculator("2 + 3 * 4")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 14)


class TestCalculatorDecimals(unittest.TestCase):
    """Test FR-3: Decimal Numbers and Float Calculations."""

    def test_decimal_addition(self):
        res = calculator("10.5 + 2.5")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 13)

    def test_decimal_multiplication(self):
        res = calculator("15.5 * 2")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 31)

    def test_decimal_division(self):
        res = calculator("100.0 / 4")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 25)

    def test_floating_precision(self):
        res = calculator("0.1 + 0.2")
        self.assertTrue(res["success"])
        self.assertAlmostEqual(res["result"], 0.3, places=7)


class TestCalculatorMathFunctionsAndConstants(unittest.TestCase):
    """Test FR-4: Mathematical Functions and Constants."""

    def test_sqrt(self):
        res = calculator("sqrt(25)")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 5)

        res144 = calculator("sqrt(144)")
        self.assertTrue(res144["success"])
        self.assertEqual(res144["result"], 12)

    def test_constants(self):
        res_pi = calculator("pi")
        self.assertTrue(res_pi["success"])
        self.assertAlmostEqual(res_pi["result"], math.pi, places=7)

        res_2pi = calculator("2 * pi")
        self.assertTrue(res_2pi["success"])
        self.assertAlmostEqual(res_2pi["result"], 2 * math.pi, places=7)

        res_e = calculator("e")
        self.assertTrue(res_e["success"])
        self.assertAlmostEqual(res_e["result"], math.e, places=7)

    def test_trigonometric_functions(self):
        res_sin = calculator("sin(0)")
        self.assertTrue(res_sin["success"])
        self.assertEqual(res_sin["result"], 0)

        res_cos = calculator("cos(0)")
        self.assertTrue(res_cos["success"])
        self.assertEqual(res_cos["result"], 1)

        res_tan = calculator("tan(0)")
        self.assertTrue(res_tan["success"])
        self.assertEqual(res_tan["result"], 0)

    def test_utility_functions(self):
        self.assertEqual(calculator("abs(-42)")["result"], 42)
        self.assertEqual(calculator("round(3.7)")["result"], 4)
        self.assertEqual(calculator("floor(3.9)")["result"], 3)
        self.assertEqual(calculator("ceil(3.1)")["result"], 4)
        self.assertEqual(calculator("log(e)")["result"], 1)


class TestCalculatorUnaryAndEdgeCases(unittest.TestCase):
    """Test Unary Operators and Edge Cases."""

    def test_unary_signs(self):
        self.assertEqual(calculator("-10")["result"], -10)
        self.assertEqual(calculator("+5")["result"], 5)
        self.assertEqual(calculator("-(-5)")["result"], 5)
        self.assertEqual(calculator("-5 + 10")["result"], 5)


class TestCalculatorInvalidInput(unittest.TestCase):
    """Test FR-5: Invalid Input Handling."""

    def test_arbitrary_words(self):
        res = calculator("hello")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_incomplete_expressions(self):
        res = calculator("10 +")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_invalid_tokens(self):
        res = calculator("abc * 5")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_empty_string(self):
        res = calculator("")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_whitespace_string(self):
        res = calculator("    ")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_non_string_input(self):
        res = calculator(12345)  # type: ignore
        self.assertFalse(res["success"])
        self.assertIn("error", res)


class TestCalculatorDivisionByZero(unittest.TestCase):
    """Test FR-6: Division and Modulo by Zero."""

    def test_division_by_zero(self):
        res = calculator("10 / 0")
        self.assertFalse(res["success"])
        self.assertIn("Division by zero is not allowed.", res["error"])

    def test_modulo_by_zero(self):
        res = calculator("10 % 0")
        self.assertFalse(res["success"])
        self.assertIn("zero", res["error"].lower())

    def test_floor_div_by_zero(self):
        res = calculator("10 // 0")
        self.assertFalse(res["success"])
        self.assertIn("zero", res["error"].lower())


class TestCalculatorSecurity(unittest.TestCase):
    """Test Section 7: Security Requirements and Code Injection Resistance."""

    def test_import_rejection(self):
        res = calculator('__import__("os")')
        self.assertFalse(res["success"])

    def test_os_system_rejection(self):
        res = calculator('__import__("os").system("dir")')
        self.assertFalse(res["success"])

    def test_open_file_rejection(self):
        res = calculator('open("calculator.py")')
        self.assertFalse(res["success"])

    def test_eval_rejection(self):
        res = calculator('eval("1 + 1")')
        self.assertFalse(res["success"])

    def test_exec_rejection(self):
        res = calculator('exec("x = 10")')
        self.assertFalse(res["success"])

    def test_list_comprehension_rejection(self):
        res = calculator('[x for x in range(10)]')
        self.assertFalse(res["success"])

    def test_lambda_rejection(self):
        res = calculator('lambda x: x + 1')
        self.assertFalse(res["success"])

    def test_attribute_traversal_rejection(self):
        res = calculator('(1).__class__.__bases__')
        self.assertFalse(res["success"])

    def test_globals_rejection(self):
        res = calculator('globals()')
        self.assertFalse(res["success"])

    def test_unsupported_function_rejection(self):
        res = calculator('system("whoami")')
        self.assertFalse(res["success"])

    def test_huge_exponent_dos_prevention(self):
        res = calculator('9 ** 99999999')
        self.assertFalse(res["success"])
        self.assertIn("exceeds maximum allowed limit", res["error"])

    def test_math_domain_error(self):
        res = calculator('sqrt(-1)')
        self.assertFalse(res["success"])
        self.assertIn("domain error", res["error"].lower())


class TestCalculatorStructure(unittest.TestCase):
    """Test Section 8: Python API structured response guarantees."""

    def test_successful_structure(self):
        res = calculator("25 * 17")
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)
        self.assertIn("expression", res)
        self.assertIn("result", res)
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 425)
        self.assertEqual(res["expression"], "25 * 17")

    def test_error_structure(self):
        res = calculator("10 / 0")
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)
        self.assertIn("expression", res)
        self.assertIn("error", res)
        self.assertFalse(res["success"])
        self.assertEqual(res["expression"], "10 / 0")


if __name__ == "__main__":
    unittest.main()
