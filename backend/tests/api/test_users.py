import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestUserEndpoints:
    """Test suite for user management endpoints."""
    
    def test_list_users_success(self, client: TestClient, auth_headers: dict, authenticated_user: dict):
        """Test successful user list retrieval."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the authenticated user
        
        # Check user data structure
        user_data = data[0]
        assert "id" in user_data
        assert "email" in user_data
        assert "full_name" in user_data
        assert "role" in user_data
        assert "is_active" in user_data
    
    def test_list_users_with_pagination(self, client: TestClient, auth_headers: dict):
        """Test user list with pagination parameters."""
        response = client.get("/api/v1/users/?skip=0&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_list_users_unauthenticated(self, client: TestClient):
        """Test user list without authentication."""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 401
    
    def test_get_user_by_id_success(self, client: TestClient, auth_headers: dict, authenticated_user: dict):
        """Test successful user retrieval by ID."""
        user_id = authenticated_user["user_id"]
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == user_id
        assert data["email"] == authenticated_user["email"]
        assert data["full_name"] == authenticated_user["full_name"]
        assert data["role"] == authenticated_user["role"]
    
    def test_get_user_not_found(self, client: TestClient, auth_headers: dict):
        """Test user retrieval with non-existent ID."""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_user_unauthenticated(self, client: TestClient, authenticated_user: dict):
        """Test user retrieval without authentication."""
        user_id = authenticated_user["user_id"]
        response = client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == 401
    
    def test_get_user_invalid_id(self, client: TestClient, auth_headers: dict):
        """Test user retrieval with invalid ID format."""
        response = client.get("/api/v1/users/invalid", headers=auth_headers)
        
        assert response.status_code == 422


class TestUserRoleAccess:
    """Test role-based access for user endpoints."""
    
    def test_trainer_can_list_users(self, client: TestClient, trainer_auth_headers: dict):
        """Test that trainers can list users."""
        response = client.get("/api/v1/users/", headers=trainer_auth_headers)
        
        assert response.status_code == 200
    
    def test_client_can_list_users(self, client: TestClient, client_auth_headers: dict):
        """Test that clients can list users."""
        response = client.get("/api/v1/users/", headers=client_auth_headers)
        
        assert response.status_code == 200
    
    def test_trainer_can_view_user_details(self, client: TestClient, trainer_auth_headers: dict, authenticated_trainer: dict):
        """Test that trainers can view user details."""
        user_id = authenticated_trainer["user_id"]
        response = client.get(f"/api/v1/users/{user_id}", headers=trainer_auth_headers)
        
        assert response.status_code == 200
    
    def test_client_can_view_user_details(self, client: TestClient, client_auth_headers: dict, authenticated_client_user: dict):
        """Test that clients can view user details."""
        user_id = authenticated_client_user["user_id"]
        response = client.get(f"/api/v1/users/{user_id}", headers=client_auth_headers)
        
        assert response.status_code == 200


class TestUserDataIntegrity:
    """Test user data integrity and validation."""
    
    def test_user_list_data_structure(self, client: TestClient, auth_headers: dict):
        """Test that user list returns proper data structure."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 200
        users = response.json()
        
        for user in users:
            # Required fields
            assert "id" in user
            assert "email" in user
            assert "full_name" in user
            assert "role" in user
            assert "is_active" in user
            assert "created_at" in user
            
            # Data types
            assert isinstance(user["id"], int)
            assert isinstance(user["email"], str)
            assert isinstance(user["full_name"], str)
            assert isinstance(user["role"], str)
            assert isinstance(user["is_active"], bool)
            assert isinstance(user["created_at"], str)
            
            # Email format validation
            assert "@" in user["email"]
            
            # Role validation
            assert user["role"] in ["trainer", "client", "admin"]
    
    def test_user_detail_data_structure(self, client: TestClient, auth_headers: dict, authenticated_user: dict):
        """Test that user detail returns proper data structure."""
        user_id = authenticated_user["user_id"]
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        user = response.json()
        
        # Required fields
        assert "id" in user
        assert "email" in user
        assert "full_name" in user
        assert "role" in user
        assert "is_active" in user
        assert "created_at" in user
        
        # Optional fields that might be present
        if "bio" in user:
            assert isinstance(user["bio"], (str, type(None)))
        if "last_login" in user:
            assert isinstance(user["last_login"], (str, type(None)))
        if "updated_at" in user:
            assert isinstance(user["updated_at"], (str, type(None)))
    
    def test_user_privacy_fields_not_exposed(self, client: TestClient, auth_headers: dict, authenticated_user: dict):
        """Test that sensitive fields are not exposed in API responses."""
        user_id = authenticated_user["user_id"]
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        user = response.json()
        
        # These fields should not be present in API responses
        assert "hashed_password" not in user
        assert "password" not in user
        assert "refresh_tokens" not in user


class TestUserPagination:
    """Test user list pagination functionality."""
    
    def test_pagination_skip_parameter(self, client: TestClient, auth_headers: dict):
        """Test pagination with skip parameter."""
        # Get all users first
        all_response = client.get("/api/v1/users/?limit=100", headers=auth_headers)
        all_users = all_response.json()
        
        if len(all_users) > 1:
            # Get users with skip=1
            skip_response = client.get("/api/v1/users/?skip=1&limit=100", headers=auth_headers)
            skip_users = skip_response.json()
            
            # Should have one less user
            assert len(skip_users) == len(all_users) - 1
            
            # First user in skip response should be second user in all response
            if len(all_users) > 1:
                assert skip_users[0]["id"] == all_users[1]["id"]
    
    def test_pagination_limit_parameter(self, client: TestClient, auth_headers: dict):
        """Test pagination with limit parameter."""
        response = client.get("/api/v1/users/?limit=1", headers=auth_headers)
        
        assert response.status_code == 200
        users = response.json()
        
        assert len(users) <= 1
    
    def test_pagination_invalid_parameters(self, client: TestClient, auth_headers: dict):
        """Test pagination with invalid parameters."""
        # Negative skip
        response = client.get("/api/v1/users/?skip=-1", headers=auth_headers)
        assert response.status_code == 422
        
        # Negative limit
        response = client.get("/api/v1/users/?limit=-1", headers=auth_headers)
        assert response.status_code == 422
    
    def test_pagination_default_values(self, client: TestClient, auth_headers: dict):
        """Test pagination with default values."""
        # No parameters should use defaults
        default_response = client.get("/api/v1/users/", headers=auth_headers)
        
        # With explicit defaults
        explicit_response = client.get("/api/v1/users/?skip=0&limit=20", headers=auth_headers)
        
        assert default_response.status_code == 200
        assert explicit_response.status_code == 200
        
        # Should return same results
        assert default_response.json() == explicit_response.json()
