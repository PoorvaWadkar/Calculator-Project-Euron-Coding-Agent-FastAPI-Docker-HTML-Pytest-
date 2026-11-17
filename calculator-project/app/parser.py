"""
Safe mathematical expression parser using Python's AST module.

WHY WE USE AST INSTEAD OF eval():
  - eval() can execute ANY Python code, including malicious imports and file deletion.
  - This parser only allows numeric literals, basic operators, and parentheses.
  - It rejects function calls, attribute access, variable names, and imports.

HOW IT WORKS:
  1. ast.parse() converts the expression string into an abstract syntax tree (AST).
  2. _safe_node() walks the tree recursively, checking every node type.
  3. Only explicitly approved node types pass through.
  4. If anything unexpected is found, a ValueError is raised.

The approved node types cover:
  - Number literals (integers, floats)
  - Unary plus and minus (+, -)
  - Binary operators (+, -, *, /, **)
  - Parentheses (represented as standalone expressions in the AST)
"""

import ast
import math

# Maximum allowed exponent base and exponent to prevent runaway computation.
MAX_EXPONENT = 1000

# Set of AST node types that are considered safe for mathematical expressions.
SAFE_NODE_TYPES = {
    ast.Expression,   # Root node wrapping the whole expression
    ast.Expr,         # Expression statement container
    ast.Constant,     # Literal values (numbers, True, False, None)
    ast.UnaryOp,      # Unary operators (+x, -x)
    ast.USub,         # Unary minus (-)
    ast.UAdd,         # Unary plus (+)
    ast.BinOp,        # Binary operators (a + b, a * b, etc.)
    ast.Add,          # Addition (+)
    ast.Sub,          # Subtraction (-)
    ast.Mult,         # Multiplication (*)
    ast.Div,          # Division (/)
    ast.Pow,          # Exponentiation (**)
}


def safe_parse(expression: str) -> float:
    """
    Safely evaluate a mathematical expression string.

    Args:
        expression: A string containing a mathematical expression,
                    e.g. "2 + 3 * 4", "-5.5", "(2 + 3) ** 2"

    Returns:
        The floating-point result of the expression.

    Raises:
        ValueError: If the expression contains anything other than
                    approved math operations, or if the result is infinite,
                    or if the expression is syntactically invalid.
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Syntax error in expression: {e}")

    # Walk the AST and only allow approved node types.
    result = _safe_node(tree)

    # Final sanity checks on the computed result.
    if not isinstance(result, (int, float)):
        raise ValueError("Expression did not produce a numeric result.")
    result = float(result)
    if math.isnan(result):
        raise ValueError("Expression produced NaN (e.g. 0/0).")
    if math.isinf(result):
        raise ValueError("Expression produced infinity (overflow or division by zero).")
    return result


def _safe_node(node: ast.AST) -> float:
    """
    Recursively walk the AST tree, evaluating only safe nodes.

    This is the core safety function. Every node type encountered is checked
    against our whitelist. Any unlisted type raises ValueError immediately.
    """
    node_type = type(node)

    # Reject any node type not in our approved list.
    if node_type not in SAFE_NODE_TYPES:
        raise ValueError(f"Disallowed expression type: {node_type.__name__}")

    # --- Root node: unwrap to the actual expression ---
    if isinstance(node, ast.Expression):
        return _safe_node(node.body)

    # --- Expression container: unwrap to the contained value ---
    if isinstance(node, ast.Expr):
        return _safe_node(node.value)

    # --- Literal constants: extract the numeric value ---
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise ValueError(
                "Only numeric literals are allowed (no strings, booleans, etc.)."
            )
        return float(node.value)

    # --- Unary operators: +x or -x ---
    if isinstance(node, ast.UnaryOp):
        operand = _safe_node(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return +operand

    # --- Binary operators: a + b, a * b, a ** b, etc. ---
    if isinstance(node, ast.BinOp):
        left = _safe_node(node.left)
        right = _safe_node(node.right)

        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            if right == 0:
                raise ValueError("Division by zero.")
            return left / right
        elif isinstance(node.op, ast.Pow):
            # Prevent unreasonable exponentiation that could cause overflow or long waits.
            if abs(left) > MAX_EXPONENT and right != 0:
                raise ValueError(
                    f"Base too large for exponentiation (max base magnitude: {MAX_EXPONENT})."
                )
            if abs(right) > MAX_EXPONENT:
                raise ValueError(
                    f"Exponent too large (max exponent magnitude: {MAX_EXPONENT})."
                )
            return left ** right

    # If we reach here, something unexpected happened.
    raise ValueError("Internal error: unhandled AST node during evaluation.")
