import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.exercise_service import ExerciseService
from app.models.exercise import Exercise, ExerciseCategory, MuscleGroup, DifficultyLevel
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseFilter


@pytest.fixture
def exercise_service():
    """Create ExerciseService instance for testing."""
    return ExerciseService()


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def sample_exercise():
    """Create a sample exercise for testing."""
    return Exercise(
        id=1,
        name="Test Exercise",
        description="Test Description",
        category=ExerciseCategory.STRENGTH.value,
        muscle_groups=["chest", "triceps"],
        equipment_needed=["dumbbells"],
        difficulty_level=DifficultyLevel.INTERMEDIATE.value,
        default_sets=3,
        default_reps="10-12",
        is_public=True,
        created_by_trainer_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestExerciseService:
    """Test suite for ExerciseService."""
    
    def test_create_exercise_success(self, exercise_service, mock_db, sample_exercise):
        """Test successful exercise creation."""
        exercise_data = ExerciseCreate(
            name="Test Exercise",
            description="Test Description",
            category=ExerciseCategory.STRENGTH,
            muscle_groups=["chest", "triceps"],
            equipment_needed=["dumbbells"],
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            default_sets=3,
            default_reps="10-12",
            is_public=True
        )
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('app.models.exercise.Exercise') as mock_exercise:
            mock_exercise.return_value = sample_exercise
            
            result = exercise_service.create_exercise(mock_db, exercise_data, trainer_id=1)
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            assert result.name == "Test Exercise"
    
    def test_get_exercise_by_id_success(self, exercise_service, mock_db, sample_exercise):
        """Test successful exercise retrieval by ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        
        result = exercise_service.get_exercise_by_id(mock_db, exercise_id=1)
        
        assert result == sample_exercise
        mock_db.query.assert_called_once()
    
    def test_get_exercise_by_id_not_found(self, exercise_service, mock_db):
        """Test exercise retrieval when exercise doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            exercise_service.get_exercise_by_id(mock_db, exercise_id=999)
        
        assert exc_info.value.status_code == 404
        assert "Exercise not found" in str(exc_info.value.detail)
    
    def test_update_exercise_success(self, exercise_service, mock_db, sample_exercise):
        """Test successful exercise update."""
        update_data = ExerciseUpdate(
            name="Updated Exercise",
            description="Updated Description"
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        result = exercise_service.update_exercise(mock_db, exercise_id=1, exercise_data=update_data, trainer_id=1)
        
        assert result.name == "Updated Exercise"
        assert result.description == "Updated Description"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_delete_exercise_success(self, exercise_service, mock_db, sample_exercise):
        """Test successful exercise deletion."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        mock_db.commit = Mock()
        
        result = exercise_service.delete_exercise(mock_db, exercise_id=1, trainer_id=1)
        
        assert result is True
        assert sample_exercise.is_active is False
        mock_db.commit.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_get_exercises_with_filter(self, exercise_service, mock_db):
        """Test getting exercises with filters."""
        exercises = [Mock(spec=Exercise) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = exercises
        mock_db.query.return_value = mock_query
        
        exercise_filter = ExerciseFilter(
            category=ExerciseCategory.STRENGTH,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            muscle_groups=["chest"]
        )
        
        result = exercise_service.get_exercises(mock_db, filters=exercise_filter, skip=0, limit=10)
        
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_search_exercises_by_name(self, exercise_service, mock_db):
        """Test searching exercises by name."""
        exercises = [Mock(spec=Exercise) for _ in range(2)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = exercises
        mock_db.query.return_value = mock_query
        
        result = exercise_service.search_exercises_by_name(mock_db, search_term="push")
        
        assert len(result) == 2
        mock_db.query.assert_called_once()
    
    def test_get_exercises_by_muscle_group(self, exercise_service, mock_db):
        """Test getting exercises by muscle group."""
        exercises = [Mock(spec=Exercise) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = exercises
        mock_db.query.return_value = mock_query
        
        result = exercise_service.get_exercises_by_muscle_group(mock_db, muscle_group="chest")
        
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_get_exercises_by_category(self, exercise_service, mock_db):
        """Test getting exercises by category."""
        exercises = [Mock(spec=Exercise) for _ in range(4)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = exercises
        mock_db.query.return_value = mock_query
        
        result = exercise_service.get_exercises_by_category(mock_db, category=ExerciseCategory.STRENGTH)
        
        assert len(result) == 4
        mock_db.query.assert_called_once()
    
    def test_unauthorized_update_attempt(self, exercise_service, mock_db, sample_exercise):
        """Test unauthorized exercise update attempt."""
        # Set different trainer_id to simulate unauthorized access
        sample_exercise.created_by_trainer_id = 2
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        
        update_data = ExerciseUpdate(name="Unauthorized Update")
        
        with pytest.raises(HTTPException) as exc_info:
            exercise_service.update_exercise(mock_db, exercise_id=1, exercise_data=update_data, trainer_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value.detail)
    
    def test_unauthorized_delete_attempt(self, exercise_service, mock_db, sample_exercise):
        """Test unauthorized exercise deletion attempt."""
        # Set different trainer_id to simulate unauthorized access
        sample_exercise.created_by_trainer_id = 2
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        
        with pytest.raises(HTTPException) as exc_info:
            exercise_service.delete_exercise(mock_db, exercise_id=1, trainer_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value.detail)
    
    def test_seed_default_exercises(self, exercise_service, mock_db):
        """Test seeding default exercises."""
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing exercises
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        exercise_service.seed_default_exercises(mock_db)
        
        # Should add multiple default exercises
        assert mock_db.add.call_count > 0
        mock_db.commit.assert_called()
