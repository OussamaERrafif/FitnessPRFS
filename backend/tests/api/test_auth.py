import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""
    
    def test_register_success(self, client: TestClient, test_user_data: dict):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["role"] == test_user_data["role"]
        assert "user_id" in data
    
    def test_register_duplicate_email(self, client: TestClient, test_user_data: dict):
        """Test registration with duplicate email."""
        # First registration
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Second registration with same email
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_register_invalid_email(self, client: TestClient, test_user_data: dict):
        """Test registration with invalid email."""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_register_weak_password(self, client: TestClient, test_user_data: dict):
        """Test registration with weak password."""
        weak_data = test_user_data.copy()
        weak_data["password"] = "123"
        
        response = client.post("/api/v1/auth/register", json=weak_data)
        
        assert response.status_code == 422
    
    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password, full_name, role
        }
        
        response = client.post("/api/v1/auth/register", json=incomplete_data)
        
        assert response.status_code == 422
    
    def test_login_success(self, client: TestClient, test_user_data: dict):
        """Test successful user login."""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()
    
    def test_login_wrong_password(self, client: TestClient, test_user_data: dict):
        """Test login with wrong password."""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "WrongPassword123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()
    
    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields."""
        login_data = {
            "email": "test@example.com"
            # Missing password
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 422
    
    def test_refresh_token_success(self, client: TestClient, authenticated_user: dict):
        """Test successful token refresh."""
        # If the fixture does not provide a refresh_token, perform login to get one
        refresh_token = authenticated_user.get("refresh_token")
        if not refresh_token:
            login_data = {
                "email": authenticated_user["email"],
                "password": authenticated_user["password"]
            }
            login_response = client.post("/api/v1/auth/login", json=login_data)
            assert login_response.status_code == 200
            refresh_token = login_response.json().get("refresh_token")
            assert refresh_token is not None

        refresh_data = {
            "refresh_token": refresh_token
        }
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh with invalid token."""
        refresh_data = {
            "refresh_token": "invalid.token.here"
        }
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
    
    def test_get_profile_success(self, client: TestClient, auth_headers: dict, authenticated_user: dict):
        """Test successful profile retrieval."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == authenticated_user["email"]
        assert data["full_name"] == authenticated_user["full_name"]
        assert data["role"] == authenticated_user["role"]
    
    def test_get_profile_unauthenticated(self, client: TestClient):
        """Test profile retrieval without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_get_profile_invalid_token(self, client: TestClient):
        """Test profile retrieval with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_update_profile_success(self, client: TestClient, auth_headers: dict):
        """Test successful profile update."""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        response = client.put("/api/v1/auth/me", headers=auth_headers, json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Updated bio"
    
    def test_update_profile_unauthenticated(self, client: TestClient):
        """Test profile update without authentication."""
        update_data = {
            "full_name": "Updated Name"
        }
        response = client.put("/api/v1/auth/me", json=update_data)
        
        assert response.status_code == 401
    
    def test_change_password_success(self, client: TestClient, auth_headers: dict, test_user_data: dict):
        """Test successful password change."""
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        response = client.post("/api/v1/auth/change-password", headers=auth_headers, json=change_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data["message"].lower()
    
    def test_change_password_wrong_current(self, client: TestClient, auth_headers: dict):
        """Test password change with wrong current password."""
        change_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        response = client.post("/api/v1/auth/change-password", headers=auth_headers, json=change_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    def test_change_password_unauthenticated(self, client: TestClient):
        """Test password change without authentication."""
        change_data = {
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        response = client.post("/api/v1/auth/change-password", json=change_data)
        
        assert response.status_code == 401
    
    def test_change_password_weak_new_password(self, client: TestClient, auth_headers: dict, test_user_data: dict):
        """Test password change with weak new password."""
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": "123",
            "confirm_password": "123"
        }
        response = client.post("/api/v1/auth/change-password", headers=auth_headers, json=change_data)
        
        assert response.status_code == 422
    
    def test_auth_flow_complete(self, client: TestClient, test_user_data: dict):
        """Test complete authentication flow."""
        # 1. Register
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        
        # 2. Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        
        # 3. Get profile
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        # 4. Update profile
        update_data = {"full_name": "Updated Name"}
        update_response = client.put("/api/v1/auth/me", headers=headers, json=update_data)
        assert update_response.status_code == 200
        
        # 5. Refresh token
        refresh_data = {"refresh_token": refresh_token}
        refresh_response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200
        
        # 6. Change password
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        change_response = client.post("/api/v1/auth/change-password", headers=headers, json=change_data)
        assert change_response.status_code == 200


class TestAuthRoleBasedAccess:
    """Test role-based access control for authentication."""
    
    def test_trainer_registration(self, client: TestClient, test_trainer_data: dict):
        """Test trainer role registration."""
        response = client.post("/api/v1/auth/register", json=test_trainer_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "trainer"
    
    def test_client_registration(self, client: TestClient, test_client_data: dict):
        """Test client role registration."""
        response = client.post("/api/v1/auth/register", json=test_client_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "client"
    
    # def test_invalid_role_registration(self, client: TestClient, test_user_data: dict):
    #     """Test registration with invalid role."""
    #     invalid_data = test_user_data.copy()
    #     invalid_data["role"] = "invalid_role"
        
    #     response = client.post("/api/v1/auth/register", json=invalid_data)
        
    #     assert response.status_code == 422


class TestAuthSecurity:
    """Test authentication security features."""
    
    def test_password_hashing(self, client: TestClient, test_user_data: dict, db: Session):
        """Test that passwords are properly hashed."""
        # Register user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        
        # Check that password is hashed in database
        from app.models.user import User
        user = db.query(User).filter(User.email == test_user_data["email"]).first()
        
        assert user is not None
        assert user.hashed_password != test_user_data["password"]
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash
    
    def test_token_expiration_format(self, client: TestClient, authenticated_user: dict):
        """Test token format and basic validation."""
        token = authenticated_user["access_token"]
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3
        
        # Each part should be base64 encoded
        import base64
        try:
            for part in parts:
                # Add padding if needed
                padded = part + "=" * (4 - len(part) % 4)
                base64.b64decode(padded)
        except Exception:
            pytest.fail("Token parts are not properly base64 encoded")


@pytest.fixture
def authenticated_user(client: TestClient, test_user_data: dict):
    # Register user
    client.post("/api/v1/auth/register", json=test_user_data)
    # Login user
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "email": test_user_data["email"],
        "full_name": test_user_data["full_name"],
        "password": test_user_data["password"],
        "role": test_user_data["role"]
    }
