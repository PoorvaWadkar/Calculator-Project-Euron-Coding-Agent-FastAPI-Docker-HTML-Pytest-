"""
Complete test suite for the Calculator API.

Tests every endpoint, including:
  - Valid calculations for all operations
  - Division by zero
  - Invalid inputs (NaN, infinity, missing fields, wrong types)
  - Safe expression parsing (valid, invalid, unsafe expressions)
  - Calculation history (storage, ordering, max 20 entries)

Each test is independent and uses FastAPI's TestClient with httpx.
Tests do NOT depend on any previous test's execution order.
"""

# The client() fixture is provided by conftest.py (resets history between tests).
from app.main import app


# =====================================================
# 1. Health Endpoint
# =====================================================

class TestHealth:
    def test_health_returns_healthy(self, client):
        """GET /health should return {"status": "healthy"}."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# =====================================================
# 2. Addition
# =====================================================

class TestAdd:
    def test_add_two_positive_numbers(self, client):
        response = client.post("/add", json={"a": 10, "b": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 15
        assert data["operation"] == "add"

    def test_add_negative_numbers(self, client):
        response = client.post("/add", json={"a": -3, "b": -7})
        assert response.status_code == 200
        assert response.json()["result"] == -10

    def test_add_zero(self, client):
        response = client.post("/add", json={"a": 0, "b": 0})
        assert response.status_code == 200
        assert response.json()["result"] == 0

    def test_add_floats(self, client):
        response = client.post("/add", json={"a": 2.5, "b": 3.7})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 6.2) < 0.001

    def test_add_missing_field(self, client):
        """Missing 'b' should return HTTP 422 (validation error)."""
        response = client.post("/add", json={"a": 10})
        assert response.status_code == 422

    def test_add_nan_input(self, client):
        """NaN values should be rejected at validation time."""
        response = client.post("/add", json={"a": "NaN", "b": 5})
        # Pydantic may return 422 for invalid float parsing of "NaN"
        assert response.status_code in (400, 422)

    def test_add_inf_input(self, client):
        """Infinity values should be rejected at validation time."""
        response = client.post("/add", json={"a": "Infinity", "b": 5})
        assert response.status_code in (400, 422)


# =====================================================
# 3. Subtraction
# =====================================================

class TestSubtract:
    def test_subtract_basic(self, client):
        response = client.post("/subtract", json={"a": 10, "b": 5})
        assert response.status_code == 200
        assert response.json()["result"] == 5
        assert response.json()["operation"] == "subtract"

    def test_subtract_negative_result(self, client):
        response = client.post("/subtract", json={"a": 3, "b": 10})
        assert response.status_code == 200
        assert response.json()["result"] == -7

    def test_subtract_missing_fields(self, client):
        response = client.post("/subtract", json={"a": 5})
        assert response.status_code == 422


# =====================================================
# 4. Multiplication
# =====================================================

class TestMultiply:
    def test_multiply_basic(self, client):
        response = client.post("/multiply", json={"a": 6, "b": 7})
        assert response.status_code == 200
        assert response.json()["result"] == 42

    def test_multiply_by_zero(self, client):
        response = client.post("/multiply", json={"a": 100, "b": 0})
        assert response.status_code == 200
        assert response.json()["result"] == 0

    def test_multiply_floats(self, client):
        response = client.post("/multiply", json={"a": 2.5, "b": 4})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 10.0) < 0.001


# =====================================================
# 5. Division
# =====================================================

class TestDivide:
    def test_divide_basic(self, client):
        response = client.post("/divide", json={"a": 10, "b": 2})
        assert response.status_code == 200
        assert response.json()["result"] == 5

    def test_divide_float_result(self, client):
        response = client.post("/divide", json={"a": 7, "b": 2})
        assert response.status_code == 200
        assert response.json()["result"] == 3.5

    def test_divide_by_zero(self, client):
        """Division by zero must return HTTP 400."""
        response = client.post("/divide", json={"a": 10, "b": 0})
        assert response.status_code == 400
        assert "zero" in response.json()["detail"].lower()

    def test_divide_missing_field(self, client):
        response = client.post("/divide", json={"a": 10})
        assert response.status_code == 422


# =====================================================
# 6. Power
# =====================================================

class TestPower:
    def test_power_basic(self, client):
        response = client.post("/power", json={"a": 2, "b": 10})
        assert response.status_code == 200
        assert response.json()["result"] == 1024

    def test_power_zero_exponent(self, client):
        response = client.post("/power", json={"a": 5, "b": 0})
        assert response.status_code == 200
        assert response.json()["result"] == 1

    def test_power_fractional_exponent(self, client):
        response = client.post("/power", json={"a": 9, "b": 0.5})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 3.0) < 0.001

    def test_power_negative_exponent(self, client):
        response = client.post("/power", json={"a": 2, "b": -1})
        assert response.status_code == 200
        assert response.json()["result"] == 0.5

    def test_power_too_large_values(self, client):
        """Extreme values should be rejected to prevent overflow."""
        response = client.post("/power", json={"a": 10000, "b": 10000})
        assert response.status_code == 400


# =====================================================
# 7. Expression Calculator (Safe AST Parser)
# =====================================================

class TestCalculate:
    def test_simple_addition(self, client):
        response = client.post("/calculate", json={"expression": "2 + 3"})
        assert response.status_code == 200
        assert response.json()["result"] == 5

    def test_operator_precedence(self, client):
        """Multiplication before addition: 2 + 3 * 4 = 14 (not 20)."""
        response = client.post("/calculate", json={"expression": "2 + 3 * 4"})
        assert response.status_code == 200
        assert response.json()["result"] == 14

    def test_parentheses(self, client):
        """(2 + 3) * 4 = 20, overriding standard precedence."""
        response = client.post("/calculate", json={"expression": "(2 + 3) * 4"})
        assert response.status_code == 200
        assert response.json()["result"] == 20

    def test_nested_parentheses(self, client):
        response = client.post("/calculate", json={"expression": "((2 + 3) * (4 - 1))"})
        assert response.status_code == 200
        assert response.json()["result"] == 15

    def test_unary_minus(self, client):
        response = client.post("/calculate", json={"expression": "-5 + 3"})
        assert response.status_code == 200
        assert response.json()["result"] == -2

    def test_complex_expression(self, client):
        response = client.post("/calculate", json={"expression": "(10 + 5) / 3 * 2"})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 10.0) < 0.001

    def test_single_number(self, client):
        response = client.post("/calculate", json={"expression": "42"})
        assert response.status_code == 200
        assert response.json()["result"] == 42

    def test_expression_with_floats(self, client):
        response = client.post("/calculate", json={"expression": "3.14 * 2"})
        assert response.status_code == 200
        assert abs(response.json()["result"] - 6.28) < 0.01

    def test_missing_expression(self, client):
        response = client.post("/calculate", json={})
        assert response.status_code == 422

    def test_empty_expression(self, client):
        response = client.post("/calculate", json={"expression": ""})
        assert response.status_code == 422

    def test_whitespace_only_expression(self, client):
        response = client.post("/calculate", json={"expression": "   "})
        assert response.status_code == 422

    def test_invalid_syntax(self, client):
        response = client.post("/calculate", json={"expression": "2 // 3"})
        assert response.status_code == 400

    def test_function_call_rejected(self, client):
        """Function calls like math.sqrt() must be rejected."""
        response = client.post("/calculate", json={"expression": "math.sqrt(16)"})
        assert response.status_code == 400

    def test_os_call_rejected(self, client):
        """__import__('os') must be rejected."""
        response = client.post("/calculate", json={"expression": "__import__('os').system('echo hacked')"})
        assert response.status_code == 400

    def test_power_in_expression(self, client):
        response = client.post("/calculate", json={"expression": "2 ** 8"})
        assert response.status_code == 200
        assert response.json()["result"] == 256

    def test_mixed_operators(self, client):
        response = client.post("/calculate", json={"expression": "10 - 3 * 2 + 4"})
        assert response.status_code == 200
        assert response.json()["result"] == 8


# =====================================================
# 8. Calculation History
# =====================================================

class TestHistory:
    def test_initial_history_empty(self, client):
        """Fresh app should have empty history."""
        response = client.get("/history")
        assert response.status_code == 200
        data = response.json()
        assert data["history"] == []
        assert data["count"] == 0

    def test_history_records_calculations(self, client):
        """History should contain recent calculations."""
        # Do some calculations first
        client.post("/add", json={"a": 1, "b": 2})
        client.post("/multiply", json={"a": 3, "b": 4})

        response = client.get("/history")
        assert response.status_code == 200
        data = response.json()
        # Should have at least 2 entries
        assert len(data["history"]) >= 2

    def test_history_has_required_fields(self, client):
        """Each history entry should have expression and result."""
        client.post("/add", json={"a": 5, "b": 10})

        response = client.get("/history")
        data = response.json()
        assert len(data["history"]) >= 1
        entry = data["history"][-1]  # Most recent
        assert "expression" in entry
        assert "result" in entry

    def test_history_response_format(self, client):
        """History response must have 'history' array and 'count' number.
        The frontend reads data.history, not the raw response object."""
        client.post("/add", json={"a": 1, "b": 2})

        response = client.get("/history")
        data = response.json()
        assert isinstance(data["history"], list)
        assert isinstance(data["count"], int)
        assert data["count"] >= 1
        assert data["history"] == [e for e in data["history"]]

    def test_history_lifo_order(self, client):
        """Most recent calculation should be last in the list."""
        client.post("/add", json={"a": 1, "b": 1})
        client.post("/multiply", json={"a": 2, "b": 3})

        response = client.get("/history")
        data = response.json()
        assert len(data["history"]) >= 2
        assert data["history"][-1]["expression"] == "2.0 * 3.0"

    def test_history_excludes_division_by_zero(self, client):
        """Failed operations (like division by zero) should NOT be recorded."""
        client.post("/add", json={"a": 1, "b": 2})
        client.post("/divide", json={"a": 10, "b": 0})  # This fails

        response = client.get("/history")
        data = response.json()
        # Only the successful add should be in history
        assert len(data["history"]) == 1
        assert data["history"][0]["expression"] == "1.0 + 2.0"

    def test_history_max_20_entries(self, client):
        """History should keep only the last 20 entries."""
        # Do 25 additions to exceed the limit of 20
        for i in range(25):
            client.post("/add", json={"a": i, "b": 1})

        response = client.get("/history")
        data = response.json()
        assert len(data["history"]) == 20  # Only the most recent 20

    def test_history_max_20_preserves_recent(self, client):
        """The 20 entries should be the most recent ones."""
        for i in range(25):
            client.post("/add", json={"a": i, "b": 1})

        response = client.get("/history")
        data = response.json()
        # The last entry should be 24 + 1 = 25 (the 25th addition, i=24)
        assert data["history"][-1]["result"] == 25
        # The first entry in history should be the 5th (i=4, since i=0..3 are evicted)
        assert data["history"][0]["result"] == 6

    def test_history_includes_calculate_endpoint(self, client):
        """The /calculate endpoint should also be recorded in history."""
        client.post("/calculate", json={"expression": "2 + 2"})

        response = client.get("/history")
        data = response.json()
        assert len(data["history"]) >= 1
        assert data["history"][-1]["result"] == 4


# =====================================================
# 9. Cross-Endpoint Edge Cases
# =====================================================

class TestEdgeCases:
    def test_nan_in_calculate(self, client):
        response = client.post("/calculate", json={"expression": "float('nan')"})
        assert response.status_code == 400

    def test_inf_in_calculate(self, client):
        response = client.post("/calculate", json={"expression": "float('inf')"})
        assert response.status_code == 400

    def test_nonexistent_endpoint(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_wrong_method(self, client):
        response = client.get("/add")
        assert response.status_code == 405


# =====================================================
# 10. Response Format Validation
# =====================================================

class TestResponseFormat:
    def test_add_response_format(self, client):
        response = client.post("/add", json={"a": 5, "b": 3})
        data = response.json()
        assert set(data.keys()) == {"operation", "a", "b", "result"}
        assert data["operation"] == "add"
        assert data["a"] == 5
        assert data["b"] == 3

    def test_calculate_response_format(self, client):
        response = client.post("/calculate", json={"expression": "2 + 2"})
        data = response.json()
        assert set(data.keys()) == {"expression", "result"}
        assert data["expression"] == "2 + 2"
