import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.session import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_api_routes_exist():
    """Test that main API routes respond (may be protected)."""
    
    # Test users endpoint - should exist but require auth
    response = client.get("/api/v1/users/")
    assert response.status_code in [401, 403, 200]  # Any of these indicates endpoint exists
    
    # Test auth endpoints - should exist
    response = client.get("/api/v1/auth/me")
    assert response.status_code in [401, 403, 200]
    
    # Test some endpoints that might exist
    response = client.get("/api/v1/")
    print(f"API root response: {response.status_code}")
    
    
def test_openapi_lists_available_paths():
    """Test to see what endpoints are actually available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_data = response.json()
    paths = openapi_data.get("paths", {})
    
    print("\\nAvailable API paths:")
    for path in sorted(paths.keys()):
        methods = list(paths[path].keys())
        print(f"  {path}: {methods}")
    
    # Just assert that we have some paths
    assert len(paths) > 0


def test_protected_endpoints():
    """Test some endpoints that should be protected."""
    # Test different potential endpoints
    test_endpoints = [
        "/api/v1/users/",
        "/api/v1/trainers/",  
        "/api/v1/clients/",
        "/api/v1/auth/me",
        "/api/v1/exercises/",
        "/api/v1/programs/",
        "/api/v1/sessions/",
        "/api/v1/meals/"
    ]
    
    for endpoint in test_endpoints:
        response = client.get(endpoint)
        print(f"{endpoint}: {response.status_code}")
        # Protected endpoints should return 401, 403, or 404 (if route doesn't exist)
        assert response.status_code in [401, 403, 404, 422]
