import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main():
    """Test that the main endpoint returns successful response."""
    response = client.get("/")
    assert response.status_code == 200


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_docs_accessible():
    """Test that the API docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test that the OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
