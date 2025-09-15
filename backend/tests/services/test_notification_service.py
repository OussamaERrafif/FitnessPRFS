import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.notification_service import NotificationService
from app.models.notification import (
    Notification, 
    NotificationTemplate, 
    NotificationPreference,
    NotificationType,
    NotificationStatus,
    NotificationCategory
)
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationTemplateCreate,
    NotificationPreferencesCreate,
    SendNotificationRequest
)


@pytest.fixture
def notification_service():
    """Create NotificationService instance for testing."""
    return NotificationService()


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def sample_notification():
    """Create a sample notification for testing."""
    return Notification(
        id=1,
        user_id=1,
        title="Test Notification",
        body="Test message",
        notification_type=NotificationType.IN_APP.value,
        category=NotificationCategory.WELCOME.value,
        status=NotificationStatus.PENDING.value,
        scheduled_for=datetime.utcnow() + timedelta(hours=1),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_template():
    """Create a sample notification template for testing."""
    return NotificationTemplate(
        id=1,
        name="test_template",
        notification_type=NotificationType.EMAIL.value,
        category=NotificationCategory.WELCOME.value,
        subject="Test Subject",
        body="Test body",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password="fake_hashed_password",
        full_name="Test User",
        phone="+1234567890"
    )


class TestNotificationService:
    """Test suite for NotificationService."""
    
    def test_create_notification_success(self, notification_service, mock_db, sample_notification):
        """Test successful notification creation."""
        notification_data = NotificationCreate(
            user_id=1,
            title="Test Notification",
            message="Test message",
            type=NotificationType.INFO,
            category=NotificationCategory.GENERAL,
            data={"key": "value"},
            scheduled_for=datetime.utcnow() + timedelta(hours=1)
        )
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('app.models.notification.Notification') as mock_notification:
            mock_notification.return_value = sample_notification
            
            result = notification_service.create_notification(mock_db, notification_data)
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            assert result.title == "Test Notification"
    
    def test_get_notification_by_id_success(self, notification_service, mock_db, sample_notification):
        """Test successful notification retrieval by ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_notification
        
        result = notification_service.get_notification_by_id(mock_db, notification_id=1)
        
        assert result == sample_notification
        mock_db.query.assert_called_once()
    
    def test_get_notification_by_id_not_found(self, notification_service, mock_db):
        """Test notification retrieval when notification doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            notification_service.get_notification_by_id(mock_db, notification_id=999)
        
        assert exc_info.value.status_code == 404
        assert "Notification not found" in str(exc_info.value.detail)
    
    def test_get_user_notifications(self, notification_service, mock_db):
        """Test getting user notifications."""
        notifications = [Mock(spec=Notification) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = notifications
        mock_db.query.return_value = mock_query
        
        result = notification_service.get_user_notifications(mock_db, user_id=1, skip=0, limit=10)
        
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_mark_notification_as_read(self, notification_service, mock_db, sample_notification):
        """Test marking notification as read."""
        sample_notification.status = NotificationStatus.PENDING
        mock_db.query.return_value.filter.return_value.first.return_value = sample_notification
        mock_db.commit = Mock()
        
        result = notification_service.mark_as_read(mock_db, notification_id=1, user_id=1)
        
        assert result.status == NotificationStatus.READ
        mock_db.commit.assert_called_once()
    
    def test_mark_notification_as_read_unauthorized(self, notification_service, mock_db, sample_notification):
        """Test marking notification as read by unauthorized user."""
        sample_notification.user_id = 2  # Different user
        mock_db.query.return_value.filter.return_value.first.return_value = sample_notification
        
        with pytest.raises(HTTPException) as exc_info:
            notification_service.mark_as_read(mock_db, notification_id=1, user_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value.detail)
    
    def test_delete_notification_success(self, notification_service, mock_db, sample_notification):
        """Test successful notification deletion."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_notification
        mock_db.delete = Mock()
        mock_db.commit = Mock()
        
        result = notification_service.delete_notification(mock_db, notification_id=1, user_id=1)
        
        assert result is True
        mock_db.delete.assert_called_once_with(sample_notification)
        mock_db.commit.assert_called_once()
    
    def test_create_template_success(self, notification_service, mock_db, sample_template):
        """Test successful template creation."""
        template_data = NotificationTemplateCreate(
            name="test_template",
            type=NotificationType.EMAIL,
            category=NotificationCategory.GENERAL,
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>",
            variables=["name", "date"]
        )
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('app.models.notification.NotificationTemplate') as mock_template:
            mock_template.return_value = sample_template
            
            result = notification_service.create_template(mock_db, template_data)
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            assert result.name == "test_template"
    
    def test_get_template_by_name(self, notification_service, mock_db, sample_template):
        """Test getting template by name."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_template
        
        result = notification_service.get_template_by_name(mock_db, template_name="test_template")
        
        assert result == sample_template
        mock_db.query.assert_called_once()
    
    def test_get_template_by_name_not_found(self, notification_service, mock_db):
        """Test getting template when it doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            notification_service.get_template_by_name(mock_db, name="nonexistent")
        
        assert exc_info.value.status_code == 404
        assert "Template not found" in str(exc_info.value.detail)
    
    @patch('smtplib.SMTP')
    def test_send_email_notification_success(self, mock_smtp, notification_service, sample_user):
        """Test successful email notification sending."""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = notification_service._send_email_notification(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test body"
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_notification_failure(self, mock_smtp, notification_service):
        """Test email notification sending failure."""
        mock_smtp.side_effect = Exception("SMTP Error")
        
        result = notification_service._send_email_notification(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test body"
        )
        
        assert result is False
    
    def test_get_pending_notifications(self, notification_service, mock_db):
        """Test getting pending notifications."""
        notifications = [Mock(spec=Notification) for _ in range(2)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = notifications
        mock_db.query.return_value = mock_query
        
        result = notification_service.get_pending_notifications(mock_db)
        
        assert len(result) == 2
        mock_db.query.assert_called_once()
    
    def test_process_scheduled_notifications(self, notification_service, mock_db):
        """Test processing scheduled notifications."""
        notifications = [Mock(spec=Notification) for _ in range(2)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = notifications
        mock_db.query.return_value = mock_query
        mock_db.commit = Mock()
        
        with patch.object(notification_service, '_send_notification') as mock_send:
            mock_send.return_value = True
            
            result = notification_service.process_scheduled_notifications(mock_db)
            
            assert result == 2  # Number of processed notifications
            assert mock_send.call_count == 2
            mock_db.commit.assert_called()
    
    def test_bulk_create_notifications(self, notification_service, mock_db):
        """Test bulk notification creation."""
        notification_data_list = [
            NotificationCreate(
                user_id=1,
                title="Notification 1",
                body="Message 1",
                notification_type=NotificationType.IN_APP.value,
                category=NotificationCategory.WELCOME.value
            ),
            NotificationCreate(
                user_id=2,
                title="Notification 2",
                body="Message 2",
                notification_type=NotificationType.IN_APP.value,
                category=NotificationCategory.WELCOME.value
            )
        ]
        
        mock_db.add_all = Mock()
        mock_db.commit = Mock()
        
        with patch('app.models.notification.Notification') as mock_notification:
            mock_notification.side_effect = [Mock(spec=Notification), Mock(spec=Notification)]
            
            result = notification_service.bulk_create_notifications(mock_db, notification_data_list)
            
            assert len(result) == 2
            mock_db.add_all.assert_called_once()
            mock_db.commit.assert_called_once()
    
    def test_get_notification_stats(self, notification_service, mock_db):
        """Test getting notification statistics."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_db.query.return_value = mock_query
        
        result = notification_service.get_notification_stats(mock_db, user_id=1)
        
        assert "total_notifications" in result
        assert "read" in result
        assert "unread" in result
        assert "pending" in result
