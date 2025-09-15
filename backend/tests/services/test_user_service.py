import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.user_service import UserService
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


@pytest.fixture
def user_service():
    """Create UserService instance for testing."""
    return UserService()


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        username="testuser",
        phone="+1234567890",
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=False,
        date_of_birth=datetime(1990, 1, 1).date(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestUserService:
    """Test suite for UserService."""
    
    def test_create_user_success(self, user_service, mock_db, sample_user):
        """Test successful user creation."""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            full_name="Test User",
            username="testuser",
            phone="+1234567890",
            role="client",
            date_of_birth=datetime(1990, 1, 1)
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('app.models.user.User') as mock_user:
            mock_user.return_value = sample_user
            with patch('app.services.user_service.AuthService.get_password_hash') as mock_hash:
                mock_hash.return_value = "hashed_password"
                
                result = user_service.create_user(mock_db, user_data)
                
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()
                assert result.email == "test@example.com"
    
    def test_create_user_email_exists(self, user_service, mock_db, sample_user):
        """Test user creation when email already exists."""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            full_name="Test User",
            username="testuser2"
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(mock_db, user_data)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
    
    def test_create_user_username_exists(self, user_service, mock_db, sample_user):
        """Test user creation when username already exists."""
        user_data = UserCreate(
            email="test2@example.com",
            password="password123",
            full_name="Test User",
            username="testuser"
        )
        
        # First query for email returns None, second for username returns existing user
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, sample_user]
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(mock_db, user_data)
        
        assert exc_info.value.status_code == 400
        assert "Username already taken" in str(exc_info.value.detail)
    
    def test_get_user_by_id_success(self, user_service, mock_db, sample_user):
        """Test successful user retrieval by ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        result = user_service.get_user_by_id(mock_db, user_id=1)
        
        assert result == sample_user
        mock_db.query.assert_called_once()
    
    def test_get_user_by_id_not_found(self, user_service, mock_db):
        """Test user retrieval when user doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_by_id(mock_db, user_id=999)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
    
    def test_get_user_by_email_success(self, user_service, mock_db, sample_user):
        """Test successful user retrieval by email."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        result = user_service.get_user_by_email(mock_db, email="test@example.com")
        
        assert result == sample_user
        mock_db.query.assert_called_once()
    
    def test_get_user_by_email_not_found(self, user_service, mock_db):
        """Test user retrieval by email when user doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = user_service.get_user_by_email(mock_db, email="nonexistent@example.com")
        
        assert result is None
    
    def test_get_user_by_username_success(self, user_service, mock_db, sample_user):
        """Test successful user retrieval by username."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        result = user_service.get_user_by_username(mock_db, username="testuser")
        
        assert result == sample_user
        mock_db.query.assert_called_once()
    
    def test_update_user_success(self, user_service, mock_db, sample_user):
        """Test successful user update."""
        update_data = UserUpdate(
            full_name="Updated Name",
            phone="+9876543210"
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        result = user_service.update_user(mock_db, user_id=1, user_data=update_data)
        
        assert result.full_name == "Updated Name"
        assert result.phone == "+9876543210"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_update_user_not_found(self, user_service, mock_db):
        """Test user update when user doesn't exist."""
        update_data = UserUpdate(full_name="Updated")
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(mock_db, user_id=999, user_data=update_data)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
    
    def test_deactivate_user_success(self, user_service, mock_db, sample_user):
        """Test successful user deactivation."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        mock_db.commit = Mock()
        
        result = user_service.deactivate_user(mock_db, user_id=1)
        
        assert result.is_active is False
        mock_db.commit.assert_called_once()
    
    def test_activate_user_success(self, user_service, mock_db, sample_user):
        """Test successful user activation."""
        sample_user.is_active = False
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        mock_db.commit = Mock()
        
        result = user_service.activate_user(mock_db, user_id=1)
        
        assert result.is_active is True
        mock_db.commit.assert_called_once()
    
    def test_verify_email_success(self, user_service, mock_db, sample_user):
        """Test successful email verification."""
        sample_user.is_verified = False
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        mock_db.commit = Mock()

        result = user_service.verify_email(mock_db, user_id=1)

        assert result.is_verified is True
        mock_db.commit.assert_called_once()
    
    def test_change_password_success(self, user_service, mock_db, sample_user):
        """Test successful password change."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        mock_db.commit = Mock()
        
        with patch('app.services.user_service.AuthService.verify_password') as mock_verify:
            mock_verify.return_value = True
            with patch('app.services.user_service.AuthService.get_password_hash') as mock_hash:
                mock_hash.return_value = "new_hashed_password"
                
                result = user_service.change_password(
                    mock_db, 
                    user_id=1, 
                    current_password="old_password", 
                    new_password="new_password"
                )
                
                assert result.hashed_password == "new_hashed_password"
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()
    
    def test_change_password_wrong_current(self, user_service, mock_db, sample_user):
        """Test password change with wrong current password."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        with patch('app.services.user_service.AuthService.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                user_service.change_password(
                    mock_db, 
                    user_id=1, 
                    current_password="wrong_password", 
                    new_password="new_password"
                )
            
            assert exc_info.value.status_code == 400
            assert "Current password is incorrect" in str(exc_info.value.detail)
    
    def test_get_users_with_pagination(self, user_service, mock_db):
        """Test getting users with pagination."""
        users = [Mock(spec=User) for _ in range(5)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = users
        mock_db.query.return_value = mock_query
        
        result = user_service.get_users(mock_db, skip=0, limit=5)
        
        assert len(result) == 5
        mock_db.query.assert_called_once()
    
    def test_search_users_by_name(self, user_service, mock_db):
        """Test searching users by name."""
        users = [Mock(spec=User) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = users
        mock_db.query.return_value = mock_query
        
        result = user_service.search_users_by_name(mock_db, search_term="John")
        
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_get_users_by_role(self, user_service, mock_db):
        """Test getting users by role."""
        users = [Mock(spec=User) for _ in range(4)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = users
        mock_db.query.return_value = mock_query
        
        result = user_service.get_users_by_role(mock_db, role=UserRole.CLIENT)
        
        assert len(result) == 4
        mock_db.query.assert_called_once()
    
    def test_get_user_count(self, user_service, mock_db):
        """Test getting total user count."""
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_db.query.return_value = mock_query
        
        result = user_service.get_user_count(mock_db)
        
        assert result == 10
        mock_db.query.assert_called_once()
    
    def test_get_active_users(self, user_service, mock_db):
        """Test getting active users only."""
        users = [Mock(spec=User) for _ in range(7)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = users
        mock_db.query.return_value = mock_query
        
        result = user_service.get_active_users(mock_db)
        
        assert len(result) == 7
        mock_db.query.assert_called_once()
    
    def test_delete_user_success(self, user_service, mock_db, sample_user):
        """Test successful user deletion."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        mock_db.delete = Mock()
        mock_db.commit = Mock()
        
        result = user_service.delete_user(mock_db, user_id=1)
        
        assert result is True
        mock_db.delete.assert_called_once_with(sample_user)
        mock_db.commit.assert_called_once()
    
    def test_delete_user_not_found(self, user_service, mock_db):
        """Test user deletion when user doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.delete_user(mock_db, user_id=999)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
