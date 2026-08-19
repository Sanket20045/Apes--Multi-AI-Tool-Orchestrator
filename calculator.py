"""
Pleximus AI Agent — Calculator Tool
====================================
A safe, reliable, and secure mathematical expression evaluator.

This module uses Python's Abstract Syntax Tree (ast) to parse and evaluate
mathematical expressions without using unrestricted eval(). It is designed
to be exposed as a local Python tool or an LLM function/tool for Gemini.
"""

import ast
import math
from typing import Any, Dict, Union

# Whitelist of allowed mathematical functions
ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "radians": math.radians,
    "degrees": math.degrees,
}

# Whitelist of allowed mathematical constants
ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}

# Maximum allowed exponent to prevent Denial of Service (DoS) / CPU freeze
MAX_EXPONENT = 10000


class EvaluationError(Exception):
    """Custom exception raised when an evaluation fails safely."""
    pass


def _safe_eval_node(node: ast.AST) -> Union[int, float]:
    """
    Recursively evaluate an AST node against safe mathematical operations.

    Args:
        node: The AST node to evaluate.

    Returns:
        The evaluated numeric result (int or float).

    Raises:
        EvaluationError: If the node contains unsupported operations or invalid values.
        ZeroDivisionError: If division or modulo by zero occurs.
    """
    # 1. Numeric Constants (Python 3.8+)
    if isinstance(node, ast.Constant):
        # Only allow int and float (reject bool, str, bytes, None, etc.)
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise EvaluationError("Only numeric constants are allowed.")

    # 2. Variable Names (Constants like pi, e, tau)
    if isinstance(node, ast.Name):
        if node.id in ALLOWED_CONSTANTS:
            return ALLOWED_CONSTANTS[node.id]
        raise EvaluationError(f"Unsupported variable or constant: '{node.id}'")

    # 3. Unary Operators (+x, -x)
    if isinstance(node, ast.UnaryOp):
        operand = _safe_eval_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise EvaluationError(f"Unsupported unary operator: {type(node.op).__name__}")

    # 4. Binary Operators (x + y, x - y, x * y, x / y, x % y, x ** y, x // y)
    if isinstance(node, ast.BinOp):
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)

        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            if right == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return left // right
        if isinstance(node.op, ast.Mod):
            if right == 0:
                raise ZeroDivisionError("Modulo by zero is not allowed.")
            return left % right
        if isinstance(node.op, ast.Pow):
            # Guard against huge power calculations that can freeze the process
            if abs(right) > MAX_EXPONENT:
                raise EvaluationError(f"Exponent exceeds maximum allowed limit ({MAX_EXPONENT}).")
            try:
                result = left ** right
                # Reject complex numbers if produced by negative base with fractional exponent
                if isinstance(result, complex):
                    raise EvaluationError("Complex numbers are not supported.")
                return result
            except OverflowError:
                raise EvaluationError("Result is too large (overflow).")

        raise EvaluationError(f"Unsupported binary operator: {type(node.op).__name__}")

    # 5. Function Calls (e.g., sqrt(144), sin(pi / 2))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise EvaluationError("Complex function calls are not supported.")

        func_name = node.func.id
        if func_name not in ALLOWED_FUNCTIONS:
            raise EvaluationError(f"Unsupported function: '{func_name}'")

        if node.keywords:
            raise EvaluationError("Keyword arguments are not supported in function calls.")

        # Evaluate arguments
        args = [_safe_eval_node(arg) for arg in node.args]
        func = ALLOWED_FUNCTIONS[func_name]

        try:
            return func(*args)
        except TypeError as e:
            raise EvaluationError(f"Invalid arguments for function '{func_name}': {e}")
        except ValueError as e:
            raise EvaluationError(f"Mathematical domain error in '{func_name}': {e}")
        except OverflowError:
            raise EvaluationError(f"Calculation overflow in '{func_name}'.")

    # Any other node type (e.g. Lambda, ListComp, Attribute, Import, Subscript, etc.) is rejected
    raise EvaluationError(f"Unsupported syntax: {type(node).__name__}")


def evaluate_expression(expression: str) -> Union[int, float]:
    """
    Safely evaluate a mathematical string expression.

    Args:
        expression: The mathematical expression string.

    Returns:
        The calculated result as int or float.

    Raises:
        ValueError: If expression is empty or invalid.
        ZeroDivisionError: If division by zero is attempted.
        EvaluationError: If unsupported syntax or domain errors occur.
    """
    if not isinstance(expression, str):
        raise ValueError("Expression must be a string.")

    cleaned_expr = expression.strip()
    if not cleaned_expr:
        raise ValueError("Expression cannot be empty.")

    try:
        # Parse the expression into an AST in 'eval' mode (single expression)
        tree = ast.parse(cleaned_expr, mode="eval")
    except SyntaxError:
        raise ValueError("Invalid mathematical expression.")

    # Evaluate the parsed AST root
    result = _safe_eval_node(tree.body)

    # Convert float values like 12.0 from sqrt(144) to int 12 if exact integer
    if isinstance(result, float) and result.is_integer() and not math.isinf(result) and not math.isnan(result):
        # Only convert if within safe integer range
        if abs(result) < 1e15:
            return int(result)

    return result


def calculator(expression: str) -> Dict[str, Any]:
    """
    Evaluate a safe mathematical expression and return a structured response.

    This function serves as the primary interface for both CLI tools
    and future LLM / Gemini function calling.

    Args:
        expression: Mathematical expression as a string.

    Returns:
        A dictionary with the following schema:
        Success:
            {
                "success": True,
                "expression": str,
                "result": Union[int, float]
            }
        Error:
            {
                "success": False,
                "expression": str,
                "error": str
            }
    """
    # Defensive handling of non-string inputs
    if not isinstance(expression, str):
        return {
            "success": False,
            "expression": str(expression),
            "error": "Expression must be a string.",
        }

    try:
        result = evaluate_expression(expression)
        return {
            "success": True,
            "expression": expression.strip(),
            "result": result,
        }
    except ZeroDivisionError as e:
        return {
            "success": False,
            "expression": expression.strip(),
            "error": str(e) if str(e) else "Division by zero is not allowed.",
        }
    except (ValueError, EvaluationError) as e:
        return {
            "success": False,
            "expression": expression.strip(),
            "error": str(e),
        }
    except Exception as e:
        # Catch-all guard to ensure the tool never crashes
        return {
            "success": False,
            "expression": expression.strip(),
            "error": f"An unexpected error occurred: {str(e)}",
        }
