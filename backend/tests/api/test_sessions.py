import pytest
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models.session_booking import SessionBooking, SessionStatus
from app.schemas.session_booking import SessionBookingCreate, SessionBookingUpdate


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_session():
    """Create a sample session booking."""
    return SessionBooking(
        id=1,
        client_id=1,
        trainer_id=1,
        scheduled_start=datetime(2024, 1, 15, 10, 0, 0),
        scheduled_end=datetime(2024, 1, 15, 11, 0, 0),
        duration_minutes=60,
        session_type="personal_training",
        status=SessionStatus.SCHEDULED,
        trainer_notes_before="Regular training session",
        price=50.0
    )


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    return {"Authorization": "Bearer test_token"}


class TestSessionEndpoints:
    """Test suite for session API endpoints."""
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.create_session_booking")
    def test_create_session_booking_success(self, mock_create, mock_get_user, client, sample_session, auth_headers):
        """Test successful session booking creation."""
        mock_get_user.return_value = Mock(id=1, role="client")
        mock_create.return_value = sample_session
        
        session_data = {
            "trainer_id": 1,
            "session_date": "2024-01-15T10:00:00",
            "duration_minutes": 60,
            "session_type": "personal_training",
            "notes": "Regular training session"
        }
        
        response = client.post("/api/v1/sessions/", json=session_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["duration_minutes"] == 60
        assert data["session_type"] == "personal_training"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_user_sessions")
    def test_get_user_sessions(self, mock_get_sessions, mock_get_user, client, sample_session, auth_headers):
        """Test getting user sessions."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_sessions.return_value = [sample_session]
        
        response = client.get("/api/v1/sessions/my-sessions", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["duration_minutes"] == 60
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_session_booking_by_id")
    def test_get_session_by_id(self, mock_get_session, mock_get_user, client, sample_session, auth_headers):
        """Test getting session by ID."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_session.return_value = sample_session
        
        response = client.get("/api/v1/sessions/1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["duration_minutes"] == 60
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.update_session_booking")
    def test_update_session_booking(self, mock_update, mock_get_user, client, sample_session, auth_headers):
        """Test updating session booking."""
        mock_get_user.return_value = Mock(id=1)
        updated_session = sample_session
        updated_session.duration_minutes = 90
        mock_update.return_value = updated_session
        
        update_data = {
            "duration_minutes": 90,
            "notes": "Extended session"
        }
        
        response = client.put("/api/v1/sessions/1", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["duration_minutes"] == 90
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.cancel_session_booking")
    def test_cancel_session_booking(self, mock_cancel, mock_get_user, client, auth_headers):
        """Test canceling session booking."""
        mock_get_user.return_value = Mock(id=1)
        cancelled_session = Mock()
        cancelled_session.status = SessionStatus.CANCELLED
        mock_cancel.return_value = cancelled_session
        
        response = client.post("/api/v1/sessions/1/cancel", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "cancelled"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.confirm_session_booking")
    def test_confirm_session_booking(self, mock_confirm, mock_get_user, client, auth_headers):
        """Test confirming session booking."""
        mock_get_user.return_value = Mock(id=1, role="trainer")
        confirmed_session = Mock()
        confirmed_session.status = SessionStatus.CONFIRMED
        mock_confirm.return_value = confirmed_session
        
        response = client.post("/api/v1/sessions/1/confirm", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "confirmed"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.complete_session_booking")
    def test_complete_session_booking(self, mock_complete, mock_get_user, client, auth_headers):
        """Test completing session booking."""
        mock_get_user.return_value = Mock(id=1, role="trainer")
        completed_session = Mock()
        completed_session.status = SessionStatus.COMPLETED
        mock_complete.return_value = completed_session
        
        completion_data = {
            "session_notes": "Great workout!",
            "trainer_feedback": "Client showed improvement"
        }
        
        response = client.post("/api/v1/sessions/1/complete", json=completion_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_trainer_sessions")
    def test_get_trainer_sessions(self, mock_get_trainer_sessions, mock_get_user, client, sample_session, auth_headers):
        """Test getting trainer sessions."""
        mock_get_user.return_value = Mock(id=1, role="trainer")
        mock_get_trainer_sessions.return_value = [sample_session]
        
        response = client.get("/api/v1/sessions/trainer/1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["trainer_id"] == 1
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_client_sessions")
    def test_get_client_sessions(self, mock_get_client_sessions, mock_get_user, client, sample_session, auth_headers):
        """Test getting client sessions."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_client_sessions.return_value = [sample_session]
        
        response = client.get("/api/v1/sessions/client/1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["client_id"] == 1
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_available_time_slots")
    def test_get_available_time_slots(self, mock_get_slots, mock_get_user, client, auth_headers):
        """Test getting available time slots."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_slots.return_value = [
            "2024-01-15T10:00:00",
            "2024-01-15T11:00:00",
            "2024-01-15T14:00:00"
        ]
        
        response = client.get("/api/v1/sessions/trainer/1/available-slots?date=2024-01-15", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert "2024-01-15T10:00:00" in data
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_sessions_by_date_range")
    def test_get_sessions_by_date_range(self, mock_get_by_date, mock_get_user, client, sample_session, auth_headers):
        """Test getting sessions by date range."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_by_date.return_value = [sample_session]
        
        response = client.get(
            "/api/v1/sessions/range?start_date=2024-01-01&end_date=2024-01-31",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.reschedule_session_booking")
    def test_reschedule_session_booking(self, mock_reschedule, mock_get_user, client, auth_headers):
        """Test rescheduling session booking."""
        mock_get_user.return_value = Mock(id=1)
        rescheduled_session = Mock()
        rescheduled_session.session_date = "2024-01-16T10:00:00"
        mock_reschedule.return_value = rescheduled_session
        
        reschedule_data = {
            "new_session_date": "2024-01-16T10:00:00",
            "reason": "Client requested change"
        }
        
        response = client.post("/api/v1/sessions/1/reschedule", json=reschedule_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_date"] == "2024-01-16T10:00:00"
    
    def test_create_session_booking_unauthorized(self, client):
        """Test creating session booking without authentication."""
        session_data = {
            "trainer_id": 1,
            "session_date": "2024-01-15T10:00:00",
            "duration_minutes": 60
        }
        
        response = client.post("/api/v1/sessions/", json=session_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch("app.api.deps.get_current_active_user")
    def test_create_session_booking_invalid_data(self, mock_get_user, client, auth_headers):
        """Test creating session booking with invalid data."""
        mock_get_user.return_value = Mock(id=1, role="client")
        
        invalid_data = {
            "trainer_id": "not_a_number",
            "session_date": "invalid_date_format",
            "duration_minutes": -30
        }
        
        response = client.post("/api/v1/sessions/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_session_statistics")
    def test_get_session_statistics(self, mock_get_stats, mock_get_user, client, auth_headers):
        """Test getting session statistics."""
        mock_get_user.return_value = Mock(id=1, role="trainer")
        mock_get_stats.return_value = {
            "total_sessions": 50,
            "completed_sessions": 45,
            "cancelled_sessions": 3,
            "upcoming_sessions": 2
        }
        
        response = client.get("/api/v1/sessions/trainer/1/stats", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_sessions"] == 50
        assert data["completed_sessions"] == 45
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.session_booking_service.session_booking_service.get_upcoming_sessions")
    def test_get_upcoming_sessions(self, mock_get_upcoming, mock_get_user, client, sample_session, auth_headers):
        """Test getting upcoming sessions."""
        mock_get_user.return_value = Mock(id=1)
        mock_get_upcoming.return_value = [sample_session]
        
        response = client.get("/api/v1/sessions/upcoming", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "scheduled"
