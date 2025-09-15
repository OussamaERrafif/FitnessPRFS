import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from app.main import app
from app.api.deps import get_current_active_user
from app.models.exercise import Exercise, ExerciseCategory, DifficultyLevel
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = Mock()
    user.id = 1
    user.role = Mock()
    user.role.value = "trainer"
    user.is_active = True
    return user


@pytest.fixture
def override_auth(mock_user):
    """Override authentication dependency."""
    def _override():
        return mock_user
    
    app.dependency_overrides[get_current_active_user] = _override
    yield _override
    app.dependency_overrides.clear()


@pytest.fixture
def sample_exercise():
    """Create a sample exercise."""
    return Exercise(
        id=1,
        name="Push-ups",
        description="Classic bodyweight exercise",
        category="strength",  # Use string value, not enum
        muscle_groups='["chest", "triceps"]',
        equipment_needed='[]',
        difficulty_level="intermediate",  # Use string value, not enum
        default_sets=3,
        default_reps="10-15",
        is_active=True,
        is_public=True,
        created_by_trainer_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        image_url=None,
        video_url=None,
        animation_url=None
    )


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    return {"Authorization": "Bearer test_token"}


class TestExerciseEndpoints:
    """Test suite for exercise API endpoints."""
    
    @patch("app.services.exercise_service.exercise_service.get_exercises")
    def test_get_exercises_success(self, mock_get_exercises, client, sample_exercise, auth_headers, override_auth):
        """Test successful retrieval of exercises."""
        mock_get_exercises.return_value = [sample_exercise]
        
        response = client.get("/api/v1/exercises/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Push-ups"
    
    @patch("app.services.exercise_service.exercise_service.get_exercises")
    def test_get_exercises_with_filters(self, mock_get_exercises, client, auth_headers, override_auth):
        """Test getting exercises with filters."""
        mock_get_exercises.return_value = []
        
        response = client.get(
            "/api/v1/exercises/?category=strength&difficulty_level=3&search=push",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_get_exercises.assert_called_once()
    
    @patch("app.services.exercise_service.exercise_service.create_exercise")
    def test_create_exercise_success(self, mock_create, client, sample_exercise, auth_headers, override_auth):
        """Test successful exercise creation."""
        mock_create.return_value = sample_exercise
        
        exercise_data = {
            "name": "Push-ups",
            "description": "Classic bodyweight exercise",
            "category": "strength",
            "muscle_groups": ["chest", "triceps"],
            "equipment_needed": [],
            "difficulty_level": "intermediate",
            "default_sets": 3,
            "default_reps": "10-15",
            "is_public": True
        }
        
        response = client.post("/api/v1/exercises/", json=exercise_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Push-ups"
    
    def test_create_exercise_unauthorized(self, client, auth_headers, mock_user):
        """Test exercise creation by non-trainer."""
        # Override the user to be a client (not trainer)
        mock_user.role.value = "client"
        
        app.dependency_overrides[get_current_active_user] = lambda: mock_user
        
        exercise_data = {
            "name": "Push-ups",
            "description": "Classic bodyweight exercise",
            "category": "strength"
        }
        
        response = client.post("/api/v1/exercises/", json=exercise_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Clean up
        app.dependency_overrides.clear()
    
    @patch("app.services.exercise_service.exercise_service.get_exercise_by_id")
    def test_get_exercise_by_id_success(self, mock_get_exercise, client, sample_exercise, auth_headers, override_auth):
        """Test successful exercise retrieval by ID."""
        mock_get_exercise.return_value = sample_exercise
        
        response = client.get("/api/v1/exercises/1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Push-ups"
    
    @patch("app.api.deps.get_current_active_user")
    @patch("app.services.exercise_service.exercise_service.get_exercise_by_id")
    def test_get_exercise_by_id_not_found(self, mock_get_exercise, mock_get_user, client, auth_headers):
        """Test exercise retrieval when exercise doesn't exist."""
        from fastapi import HTTPException
        mock_get_user.return_value = Mock(id=1)
        mock_get_exercise.side_effect = HTTPException(status_code=404, detail="Exercise not found")
        
        response = client.get("/api/v1/exercises/999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch("app.services.exercise_service.exercise_service.update_exercise")
    def test_update_exercise_success(self, mock_update, client, sample_exercise, auth_headers, override_auth):
        """Test successful exercise update."""
        updated_exercise = sample_exercise
        updated_exercise.name = "Updated Push-ups"
        mock_update.return_value = updated_exercise
        
        update_data = {
            "name": "Updated Push-ups",
            "description": "Updated description"
        }
        
        response = client.put("/api/v1/exercises/1", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Push-ups"
    
    @patch("app.services.exercise_service.exercise_service.delete_exercise")
    def test_delete_exercise_success(self, mock_delete, client, auth_headers, override_auth):
        """Test successful exercise deletion."""
        mock_delete.return_value = True
        
        response = client.delete("/api/v1/exercises/1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    @patch("app.services.exercise_service.exercise_service.search_exercises")
    def test_search_exercises(self, mock_search, client, sample_exercise, auth_headers, override_auth):
        """Test exercise search functionality."""
        mock_search.return_value = [sample_exercise]
        
        response = client.get("/api/v1/exercises/search?search_term=push", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Push-ups"
    
    @patch("app.services.exercise_service.exercise_service.get_exercises_by_muscle_group")
    def test_get_exercises_by_muscle_group(self, mock_get_by_muscle, client, sample_exercise, auth_headers, override_auth):
        """Test getting exercises by muscle group."""
        mock_get_by_muscle.return_value = [sample_exercise]
        
        response = client.get("/api/v1/exercises/by-muscle/chest", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Push-ups"
    
    def test_get_exercises_unauthorized(self, client):
        """Test getting exercises without authentication."""
        response = client.get("/api/v1/exercises/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_exercise_without_auth(self, client):
        """Test creating exercise without authentication."""
        exercise_data = {
            "name": "Push-ups",
            "description": "Classic bodyweight exercise"
        }
        
        response = client.post("/api/v1/exercises/", json=exercise_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_exercise_invalid_data(self, client, auth_headers, override_auth):
        """Test exercise creation with invalid data."""
        
        invalid_data = {
            "description": "Missing name field"
        }
        
        response = client.post("/api/v1/exercises/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.services.exercise_service.exercise_service.get_exercises")
    def test_get_exercises_pagination(self, mock_get_exercises, client, auth_headers, override_auth):
        """Test exercise pagination parameters."""
        mock_get_exercises.return_value = []
        
        response = client.get("/api/v1/exercises/?skip=10&limit=20", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        mock_get_exercises.assert_called_once()
        # Verify skip and limit parameters were passed correctly
        call_args = mock_get_exercises.call_args
        assert call_args[0][1] == 10  # skip
        assert call_args[0][2] == 20  # limit
