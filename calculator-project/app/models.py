"""
Pydantic request and response models for the calculator API.

This module defines the data structures that FastAPI uses to:
  1. Validate incoming JSON request bodies.
  2. Ensure numeric fields are valid (not NaN or infinity).
"""

import math
from pydantic import BaseModel, field_validator


class CalcRequest(BaseModel):
    """Shared request model for the two-number endpoints (/add, /subtract, etc).

    Accepts two floating-point numbers `a` and `b`.
    Rejects NaN and infinity values at validation time.
    """

    a: float
    b: float

    @field_validator("a", "b")
    @classmethod
    def reject_non_finite(cls, value: float) -> float:
        """Raise if the value is NaN or infinity (mathematically meaningless here)."""
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Values must be finite numbers (no NaN or infinity).")
        return value


class CalcExpression(BaseModel):
    """Request model for the /calculate endpoint.

    Accepts a single string expression like '2 + 3 * 4'.
    The parser.py module handles the actual safe evaluation.
    """

    expression: str

    @field_validator("expression")
    @classmethod
    def reject_empty_or_giant(cls, value: str) -> str:
        """Reject empty strings and absurdly long expressions (>500 chars)."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Expression must not be empty.")
        if len(stripped) > 500:
            raise ValueError("Expression is too long (max 500 characters).")
        return stripped


class CalcResponse(BaseModel):
    """Standard response model for the two-number endpoints.

    Returns the original inputs, the operation name, and the numeric result.
    """

    operation: str
    a: float
    b: float
    result: float


class ExprResponse(BaseModel):
    """Response model for the /calculate endpoint.

    Returns the original expression string and its evaluated result.
    """

    expression: str
    result: float


class HistoryEntry(BaseModel):
    """One entry stored in the in-memory calculation history.

    Contains:
      - expression: what was calculated (e.g. '10 + 5' or '2 + 3 * 4')
      - result: the numeric result of that expression
    """

    expression: str
    result: float
