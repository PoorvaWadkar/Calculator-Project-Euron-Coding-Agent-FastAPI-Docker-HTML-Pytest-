"""
Pytest configuration for the Calculator API.

Provides a shared fixture that:
  1. Creates a Starlette TestClient for the FastAPI app.
  2. Resets the in-memory calculation history before every test
     so that history-related tests start with a clean slate.
"""

import pytest
from fastapi.testclient import TestClient

# Import the app and the module-level history deque to reset it.
from app.main import app, history


@pytest.fixture
def client():
    """Provide a TestClient and reset history before each test."""
    history.clear()  # Clean slate for every test.
    return TestClient(app)

