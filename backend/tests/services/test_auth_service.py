import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.auth_service import auth_service
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest


class TestAuthService:
    """Test suite for AuthService."""
    
    def test_verify_password_success(self):
        """Test successful password verification."""
        plain_password = "TestPassword123!"
        hashed_password = auth_service.get_password_hash(plain_password)
        
        result = auth_service.verify_password(plain_password, hashed_password)
        
        assert result is True
    
    def test_verify_password_failure(self):
        """Test failed password verification."""
        plain_password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed_password = auth_service.get_password_hash(plain_password)
        
        result = auth_service.verify_password(wrong_password, hashed_password)
        
        assert result is False
    
    def test_get_password_hash(self):
        """Test password hashing."""
        password = "TestPassword123!"
        
        hashed = auth_service.get_password_hash(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt hash format
        assert len(hashed) > 50  # bcrypt hashes are long
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "user@example.com", "user_id": 1}
        expires_delta = timedelta(minutes=30)
        
        token = auth_service.create_access_token(data, expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
        # JWT tokens have 3 parts separated by dots
        assert len(token.split(".")) == 3
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        
        token = auth_service.create_refresh_token(user)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split(".")) == 3
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        data = {"sub": "user@example.com", "user_id": 1}
        token = auth_service.create_access_token(data)
        
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user@example.com"
        assert payload["user_id"] == 1
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = auth_service.verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        data = {"sub": "user@example.com", "user_id": 1}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = auth_service.create_access_token(data, expires_delta)
        
        payload = auth_service.verify_token(token)
        
        assert payload is None
    
    def test_register_user_success(self, db: Session):
        """Test successful user registration."""
        email = "test@example.com"
        username = "testuser"
        password = "TestPassword123!"
        full_name = "Test User"
        role = UserRole.TRAINER
        
        user = auth_service.register_user(db, email, username, password, full_name, role)
        
        assert user is not None
        assert user.email == email
        assert user.username == username
        assert user.full_name == full_name
        assert user.role == role
        assert user.hashed_password != password  # Should be hashed
        assert auth_service.verify_password(password, user.hashed_password)
    
    def test_register_user_duplicate_email(self, db: Session):
        """Test user registration with duplicate email."""
        email = "duplicate@example.com"
        
        # Register first user
        auth_service.register_user(db, email, "user1", "password1", "User 1", UserRole.TRAINER)
        
        # Try to register second user with same email
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(db, email, "user2", "password2", "User 2", UserRole.CLIENT)
        
        assert exc_info.value.status_code == 400
        assert "already registered" in str(exc_info.value.detail).lower()
    
    def test_register_user_duplicate_username(self, db: Session):
        """Test user registration with duplicate username."""
        username = "duplicateuser"
        
        # Register first user
        auth_service.register_user(db, "user1@example.com", username, "password1", "User 1", UserRole.TRAINER)
        
        # Try to register second user with same username
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(db, "user2@example.com", username, "password2", "User 2", UserRole.CLIENT)
        
        assert exc_info.value.status_code == 400
        assert "username" in str(exc_info.value.detail).lower()
    
    def test_authenticate_user_success(self, db: Session):
        """Test successful user authentication."""
        email = "auth@example.com"
        password = "AuthPassword123!"
        
        # Register user first
        user = auth_service.register_user(db, email, "authuser", password, "Auth User", UserRole.TRAINER)
        
        # Authenticate
        authenticated_user = auth_service.authenticate_user(db, email, password)
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.email == email
    
    def test_authenticate_user_wrong_email(self, db: Session):
        """Test authentication with wrong email."""
        result = auth_service.authenticate_user(db, "nonexistent@example.com", "password")
        
        assert result is None
    
    def test_authenticate_user_wrong_password(self, db: Session):
        """Test authentication with wrong password."""
        email = "wrongpass@example.com"
        password = "CorrectPassword123!"
        
        # Register user
        auth_service.register_user(db, email, "wrongpass", password, "Wrong Pass User", UserRole.TRAINER)
        
        # Try to authenticate with wrong password
        result = auth_service.authenticate_user(db, email, "WrongPassword123!")
        
        assert result is None
    
    def test_authenticate_user_inactive(self, db: Session):
        """Test authentication with inactive user."""
        email = "inactive@example.com"
        password = "InactivePassword123!"
        
        # Register user and deactivate
        user = auth_service.register_user(db, email, "inactive", password, "Inactive User", UserRole.TRAINER)
        user.is_active = False
        db.commit()
        
        # Try to authenticate
        result = auth_service.authenticate_user(db, email, password)
        
        # Should still return user but caller should check is_active
        assert result is not None
        assert result.is_active is False
    
    def test_get_user_by_id_success(self, db: Session):
        """Test successful user retrieval by ID."""
        # Register user
        user = auth_service.register_user(db, "byid@example.com", "byid", "password", "By ID User", UserRole.TRAINER)
        
        # Get by ID
        retrieved_user = auth_service.get_user_by_id(db, user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
    
    def test_get_user_by_id_not_found(self, db: Session):
        """Test user retrieval with non-existent ID."""
        result = auth_service.get_user_by_id(db, 99999)
        
        assert result is None
    
    def test_get_user_by_email_success(self, db: Session):
        """Test successful user retrieval by email."""
        email = "byemail@example.com"
        user = auth_service.register_user(db, email, "byemail", "password", "By Email User", UserRole.TRAINER)
        
        retrieved_user = auth_service.get_user_by_email(db, email)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == email
    
    def test_get_user_by_email_not_found(self, db: Session):
        """Test user retrieval with non-existent email."""
        result = auth_service.get_user_by_email(db, "nonexistent@example.com")
        
        assert result is None
    
    def test_create_user_tokens(self, db: Session):
        """Test user token creation."""
        user = auth_service.register_user(db, "tokens@example.com", "tokens", "password", "Tokens User", UserRole.TRAINER)
        
        tokens = auth_service.create_user_tokens(user)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"
        
        # Verify tokens are valid
        access_payload = auth_service.verify_token(tokens["access_token"])
        assert access_payload is not None
        assert access_payload["user_id"] == user.id
    
    def test_refresh_access_token_success(self, db: Session):
        """Test successful token refresh."""
        user = auth_service.register_user(db, "refresh@example.com", "refresh", "password", "Refresh User", UserRole.TRAINER)
        tokens = auth_service.create_user_tokens(user)
        refresh_token = tokens["refresh_token"]
        
        new_tokens = auth_service.refresh_access_token(db, refresh_token)
        
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]  # Should be different
    
    def test_refresh_access_token_invalid(self, db: Session):
        """Test token refresh with invalid token."""
        invalid_token = "invalid.refresh.token"
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.refresh_access_token(db, invalid_token)
        
        assert exc_info.value.status_code == 401


class TestAuthServiceEdgeCases:
    """Test edge cases and error conditions for AuthService."""
    
    def test_register_user_empty_email(self, db: Session):
        """Test registration with empty email."""
        with pytest.raises((HTTPException, ValueError)):
            auth_service.register_user(db, "", "username", "password", "Name", UserRole.TRAINER)
    
    def test_register_user_empty_password(self, db: Session):
        """Test registration with empty password."""
        with pytest.raises((HTTPException, ValueError)):
            auth_service.register_user(db, "test@example.com", "username", "", "Name", UserRole.TRAINER)
    
    def test_verify_password_empty_strings(self):
        """Test password verification with empty strings."""
        result1 = auth_service.verify_password("", "")
        result2 = auth_service.verify_password("password", "")
        result3 = auth_service.verify_password("", "hash")
        
        assert result1 is False
        assert result2 is False
        assert result3 is False
    
    def test_token_with_special_characters(self):
        """Test token creation with special characters in data."""
        data = {
            "sub": "user+special@example.com",
            "user_id": 1,
            "special": "ñáéíóú"
        }
        
        token = auth_service.create_access_token(data)
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == data["sub"]
        assert payload["special"] == data["special"]
    
    def test_register_user_with_extreme_values(self, db: Session):
        """Test registration with extreme but valid values."""
        # Very long but valid email
        long_email = "a" * 50 + "@" + "b" * 50 + ".com"
        long_name = "Name " * 20  # Very long name
        
        user = auth_service.register_user(
            db, long_email, "longuser", "ValidPassword123!", long_name, UserRole.TRAINER
        )
        
        assert user is not None
        assert user.email == long_email
        assert user.full_name == long_name
    
    @patch('app.services.auth_service.datetime')
    def test_token_creation_time_dependency(self, mock_datetime):
        """Test token creation time dependency."""
        # Mock datetime to return fixed time
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time
        
        data = {"sub": "test@example.com", "user_id": 1}
        token = auth_service.create_access_token(data)
        
        # Token should be created successfully with mocked time
        assert token is not None
        assert isinstance(token, str)


class TestAuthServiceSecurity:
    """Test security aspects of AuthService."""
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "SamePassword123!"
        
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert auth_service.verify_password(password, hash1)
        assert auth_service.verify_password(password, hash2)
    
    def test_token_payload_integrity(self):
        """Test that token payloads can't be tampered with."""
        data = {"sub": "test@example.com", "user_id": 1}
        token = auth_service.create_access_token(data)
        
        # Tamper with token (change last character)
        tampered_token = token[:-1] + "X"
        
        # Verification should fail
        payload = auth_service.verify_token(tampered_token)
        assert payload is None
    
    def test_sensitive_data_not_in_tokens(self):
        """Test that sensitive data is not included in tokens."""
        data = {
            "sub": "test@example.com",
            "user_id": 1,
            "role": "trainer"
        }
        token = auth_service.create_access_token(data)
        payload = auth_service.verify_token(token)
        
        # Ensure no sensitive data in payload
        assert "password" not in payload
        assert "hashed_password" not in payload
        assert "secret" not in payload
