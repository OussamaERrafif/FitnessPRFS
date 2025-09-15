import pytest
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationCategory
from app.schemas.notification import NotificationCreate, SendNotificationRequest


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_notification():
    """Create a sample notification."""
    return Notification(
        id=1,
        user_id=1,
        title="Welcome to FitnessPR!",
        body="Welcome to our fitness platform. Start your journey today!",
        notification_type=NotificationType.EMAIL,
        category=NotificationCategory.WELCOME,
        status=NotificationStatus.PENDING,
        template_variables={"onboarding_step": 1},
        created_at=datetime(2024, 1, 15, 10, 0, 0)
    )


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    return {"Authorization": "Bearer test_token"}


class TestNotificationEndpoints:
    """Test suite for notification API endpoints."""
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.create_notification")
    def test_create_notification_success(self, mock_create, mock_get_user, client, sample_notification, auth_headers):
        """Test successful notification creation."""
        mock_get_user.return_value = Mock(id=1, role="admin")
        mock_create.return_value = sample_notification
        
        notification_data = {
            "user_id": 1,
            "title": "Welcome to FitnessPR!",
            "message": "Welcome to our fitness platform. Start your journey today!",
            "type": "email",
            "category": "welcome",
            "data": {"onboarding_step": 1}
        }
        
        response = client.post("/api/v1/notifications/", json=notification_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Welcome to FitnessPR!"
        assert data["type"] == "email"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_user_notifications")
    def test_get_user_notifications(self, mock_get_notifications, mock_get_user, client, sample_notification, auth_headers):
        """Test getting user notifications."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_notifications.return_value = [sample_notification]
        
        response = client.get("/api/v1/notifications/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Welcome to FitnessPR!"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_notification_by_id")
    def test_get_notification_by_id(self, mock_get_notification, mock_get_user, client, sample_notification, auth_headers):
        """Test getting notification by ID."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_notification.return_value = sample_notification
        
        response = client.get("/api/v1/notifications/1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Welcome to FitnessPR!"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.mark_as_read")
    def test_mark_notification_as_read(self, mock_mark_read, mock_get_user, client, auth_headers):
        """Test marking notification as read."""
        mock_get_user.return_value = Mock(id=1)
        read_notification = Mock()
        read_notification.status = NotificationStatus.READ
        mock_mark_read.return_value = read_notification
        
        response = client.post("/api/v1/notifications/1/read", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "read"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.mark_all_as_read")
    def test_mark_all_notifications_as_read(self, mock_mark_all_read, mock_get_user, client, auth_headers):
        """Test marking all notifications as read."""
        mock_get_user.return_value = Mock(id=1)
        mock_mark_all_read.return_value = {"marked_count": 5}
        
        response = client.post("/api/v1/notifications/mark-all-read", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["marked_count"] == 5
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.delete_notification")
    def test_delete_notification(self, mock_delete, mock_get_user, client, auth_headers):
        """Test deleting notification."""
        mock_get_user.return_value = Mock(id=1)
        mock_delete.return_value = True
        
        response = client.delete("/api/v1/notifications/1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.send_notification")
    def test_send_notification(self, mock_send, mock_get_user, client, auth_headers):
        """Test sending notification immediately."""
        mock_get_user.return_value = Mock(id=1, role="trainer")
        mock_send.return_value = {"sent": True, "message": "Notification sent successfully"}
        
        send_data = {
            "user_id": 2,
            "title": "Session Reminder",
            "message": "Your session is in 1 hour",
            "type": "push",
            "send_immediately": True
        }
        
        response = client.post("/api/v1/notifications/send", json=send_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sent"] is True
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_notification_stats")
    def test_get_notification_stats(self, mock_get_stats, mock_get_user, client, auth_headers):
        """Test getting notification statistics."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_stats.return_value = {
            "total": 10,
            "read": 7,
            "unread": 3,
            "pending": 2
        }
        
        response = client.get("/api/v1/notifications/stats", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 10
        assert data["unread"] == 3
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_notifications_by_category")
    def test_get_notifications_by_category(self, mock_get_by_category, mock_get_user, client, sample_notification, auth_headers):
        """Test getting notifications by category."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_by_category.return_value = [sample_notification]
        
        response = client.get("/api/v1/notifications/category/welcome", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "welcome"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_notifications_by_type")
    def test_get_notifications_by_type(self, mock_get_by_type, mock_get_user, client, sample_notification, auth_headers):
        """Test getting notifications by type."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_by_type.return_value = [sample_notification]
        
        response = client.get("/api/v1/notifications/type/email", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "email"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_unread_notifications")
    def test_get_unread_notifications(self, mock_get_unread, mock_get_user, client, sample_notification, auth_headers):
        """Test getting unread notifications."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_unread.return_value = [sample_notification]
        
        response = client.get("/api/v1/notifications/unread", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.bulk_create_notifications")
    def test_bulk_create_notifications(self, mock_bulk_create, mock_get_user, client, auth_headers):
        """Test bulk creation of notifications."""
        mock_get_user.return_value = Mock(id=1, role="admin")
        mock_bulk_create.return_value = [Mock(), Mock(), Mock()]
        
        bulk_data = [
            {
                "user_id": 1,
                "title": "Notification 1",
                "message": "Message 1",
                "type": "email"
            },
            {
                "user_id": 2,
                "title": "Notification 2",
                "message": "Message 2",
                "type": "push"
            },
            {
                "user_id": 3,
                "title": "Notification 3",
                "message": "Message 3",
                "type": "sms"
            }
        ]
        
        response = client.post("/api/v1/notifications/bulk", json=bulk_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data) == 3
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.schedule_notification")
    def test_schedule_notification(self, mock_schedule, mock_get_user, client, auth_headers):
        """Test scheduling notification for future delivery."""
        mock_get_user.return_value = Mock(id=1, role="trainer")
        scheduled_notification = Mock()
        scheduled_notification.scheduled_for = "2024-01-16T10:00:00"
        mock_schedule.return_value = scheduled_notification
        
        schedule_data = {
            "user_id": 2,
            "title": "Session Reminder",
            "message": "Your session is tomorrow",
            "type": "push",
            "scheduled_for": "2024-01-16T10:00:00"
        }
        
        response = client.post("/api/v1/notifications/schedule", json=schedule_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["scheduled_for"] == "2024-01-16T10:00:00"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_notification_preferences")
    def test_get_notification_preferences(self, mock_get_prefs, mock_get_user, client, auth_headers):
        """Test getting user notification preferences."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_prefs.return_value = {
            "email_enabled": True,
            "push_enabled": True,
            "sms_enabled": False,
            "categories": {
                "sessions": True,
                "progress": True,
                "marketing": False
            }
        }
        
        response = client.get("/api/v1/notifications/preferences", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email_enabled"] is True
        assert data["categories"]["marketing"] is False
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.update_notification_preferences")
    def test_update_notification_preferences(self, mock_update_prefs, mock_get_user, client, auth_headers):
        """Test updating user notification preferences."""
        mock_get_user.return_value = Mock(id=1)
        updated_prefs = Mock()
        updated_prefs.email_enabled = False
        mock_update_prefs.return_value = updated_prefs
        
        prefs_data = {
            "email_enabled": False,
            "push_enabled": True,
            "categories": {
                "sessions": True,
                "progress": True,
                "marketing": False
            }
        }
        
        response = client.put("/api/v1/notifications/preferences", json=prefs_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email_enabled"] is False
    
    def test_get_notifications_unauthorized(self, client):
        """Test getting notifications without authentication."""
        response = client.get("/api/v1/notifications/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch("app.api.deps.get_current_active_user")
    def test_create_notification_forbidden_for_regular_user(self, mock_get_user, client, auth_headers):
        """Test creating notification as regular user (should be forbidden)."""
        mock_get_user.return_value = Mock(id=1, role="client")
        
        notification_data = {
            "user_id": 2,
            "title": "Test Notification",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/notifications/", json=notification_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch("app.api.deps.get_current_active_user")
    def test_create_notification_invalid_data(self, mock_get_user, client, auth_headers):
        """Test creating notification with invalid data."""
        mock_get_user.return_value = Mock(id=1, role="admin")
        
        invalid_data = {
            "user_id": "not_a_number",
            "title": "",  # Empty title
            "type": "invalid_type"
        }
        
        response = client.post("/api/v1/notifications/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.notification_service.notification_service.get_pending_notifications")
    def test_get_pending_notifications_admin_only(self, mock_get_pending, mock_get_user, client, sample_notification, auth_headers):
        """Test getting pending notifications (admin only)."""
        mock_get_user.return_value = Mock(id=1, role="admin")
        mock_get_pending.return_value = [sample_notification]
        
        response = client.get("/api/v1/notifications/pending", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"
