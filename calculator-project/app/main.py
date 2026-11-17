"""
Calculator API — FastAPI application.

This is the main application module. It wires together:
  - Pydantic models (from models.py) for request/response validation
  - The safe expression parser (from parser.py) for /calculate
  - An in-memory deque for calculation history

Endpoints:
  GET  /health       — Application health check
  POST /add          — Add two numbers
  POST /subtract     — Subtract two numbers
  POST /multiply     — Multiply two numbers
  POST /divide       — Divide two numbers (400 on division by zero)
  POST /power        — Raise a to the power of b
  POST /calculate    — Safe expression evaluation (e.g. "2 + 3 * 4")
  GET  /history      — Last 20 calculations
"""

from collections import deque
from math import isinf, isnan

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import CalcExpression, CalcRequest, CalcResponse, ExprResponse, HistoryEntry
from .parser import safe_parse

# --- Application Setup ---

app = FastAPI(
    title="Calculator API",
    description="A simple calculator with basic operations, safe expression parsing, and in-memory history.",
    version="1.0.0",
)

# Serve static files (calculator frontend)
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def serve_frontend():
    """Serve the calculator frontend."""
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)

# --- In-Memory Calculation History ---
# We use a deque with maxlen=20 to automatically keep only the most recent 20 entries.
# NOTE: This history resets every time the application restarts (no database).
history: deque[HistoryEntry] = deque(maxlen=20)


# --- Helper Functions ---

def _add_to_history(expression: str, result: float) -> None:
    """Append a successful calculation to the in-memory history."""
    history.append(HistoryEntry(expression=expression, result=result))


def _check_finite_result(result: float) -> float:
    """Verify the result is a finite number; raise HTTP 400 otherwise."""
    if isnan(result) or isinf(result):
        raise HTTPException(
            status_code=400,
            detail="Result is not a finite number (overflow or undefined).",
        )
    return result


def _do_operation(op_name: str, a: float, b: float) -> float:
    """Execute a two-number math operation.

    Args:
        op_name: One of 'add', 'subtract', 'multiply', 'divide', 'power'.
        a: The first operand.
        b: The second operand.

    Returns:
        The computed result.

    Raises:
        HTTPException: If the operation is invalid (e.g. division by zero).
    """
    if op_name == "add":
        return a + b
    elif op_name == "subtract":
        return a - b
    elif op_name == "multiply":
        return a * b
    elif op_name == "divide":
        if b == 0:
            raise HTTPException(
                status_code=400,
                detail="Division by zero is not allowed.",
            )
        return a / b
    elif op_name == "power":
        # Guard against extreme exponentiation that could overflow or hang.
        if abs(a) > 1000 and abs(b) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Power operation values too large; this could cause overflow.",
            )
        return a ** b
    else:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {op_name}")


def _build_response(op_name: str, a: float, b: float, result: float) -> CalcResponse:
    """Build a standard CalcResponse with the operation name and values."""
    return CalcResponse(operation=op_name, a=a, b=b, result=result)


# --- Endpoints ---

@app.get("/health")
def health_check():
    """Application health check endpoint.

    Returns:
        {"status": "healthy"} if the application is running.
    """
    return {"status": "healthy"}


@app.post("/add")
def add_numbers(calc: CalcRequest):
    """Add two numbers together.

    Request body: {"a": 10, "b": 5}
    Response:     {"operation": "add", "a": 10, "b": 5, "result": 15}
    """
    result = _check_finite_result(_do_operation("add", calc.a, calc.b))
    _add_to_history(f"{calc.a} + {calc.b}", result)
    return _build_response("add", calc.a, calc.b, result)


@app.post("/subtract")
def subtract_numbers(calc: CalcRequest):
    """Subtract the second number from the first.

    Request body: {"a": 10, "b": 5}
    Response:     {"operation": "subtract", "a": 10, "b": 5, "result": 5}
    """
    result = _check_finite_result(_do_operation("subtract", calc.a, calc.b))
    _add_to_history(f"{calc.a} - {calc.b}", result)
    return _build_response("subtract", calc.a, calc.b, result)


@app.post("/multiply")
def multiply_numbers(calc: CalcRequest):
    """Multiply two numbers.

    Request body: {"a": 10, "b": 5}
    Response:     {"operation": "multiply", "a": 10, "b": 5, "result": 50}
    """
    result = _check_finite_result(_do_operation("multiply", calc.a, calc.b))
    _add_to_history(f"{calc.a} * {calc.b}", result)
    return _build_response("multiply", calc.a, calc.b, result)


@app.post("/divide")
def divide_numbers(calc: CalcRequest):
    """Divide the first number by the second.

    Returns HTTP 400 if b is zero.

    Request body: {"a": 10, "b": 5}
    Response:     {"operation": "divide", "a": 10, "b": 5, "result": 2}
    """
    result = _check_finite_result(_do_operation("divide", calc.a, calc.b))
    _add_to_history(f"{calc.a} / {calc.b}", result)
    return _build_response("divide", calc.a, calc.b, result)


@app.post("/power")
def power_numbers(calc: CalcRequest):
    """Raise the first number to the power of the second.

    Request body: {"a": 2, "b": 10}
    Response:     {"operation": "power", "a": 2, "b": 10, "result": 1024}
    """
    result = _check_finite_result(_do_operation("power", calc.a, calc.b))
    _add_to_history(f"{calc.a} ** {calc.b}", result)
    return _build_response("power", calc.a, calc.b, result)


@app.post("/calculate")
def calculate_expression(expr: CalcExpression):
    """Evaluate a mathematical expression safely using the AST parser.

    Supports: +, -, *, /, ** and parentheses.
    Follows standard mathematical operator precedence.
    Does NOT use eval() — uses a safe AST-based parser.

    Request body: {"expression": "2 + 3 * 4"}
    Response:     {"expression": "2 + 3 * 4", "result": 14}
    """
    try:
        result = safe_parse(expr.expression)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result = _check_finite_result(result)
    _add_to_history(expr.expression, result)
    return ExprResponse(expression=expr.expression, result=result)


@app.get("/history")
def get_history():
    """Return the most recent 20 calculations.

    History is stored in memory and resets on application restart.

    Response: {"history": [...], "count": <number>}
    """
    entries = list(history)  # Convert deque to a list for JSON serialization.
    return {"history": entries, "count": len(entries)}


# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
