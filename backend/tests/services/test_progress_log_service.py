import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.progress_log_service import ProgressLogService
from app.models.progress_log import ProgressLog, WorkoutType, LogType, ProgressType
from app.schemas.progress_log import ProgressLogCreate, ProgressLogUpdate


@pytest.fixture
def progress_log_service():
    """Create ProgressLogService instance for testing."""
    return ProgressLogService()


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def sample_progress_log():
    """Create a sample progress log for testing."""
    return ProgressLog(
        id=1,
        user_id=1,
        exercise_id=1,
        workout_type="strength",
        sets=3,
        reps="10,8,6",
        weight=75.5,
        notes="Great progress!",
        workout_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestProgressLogService:
    """Test suite for ProgressLogService."""
    
    def test_create_progress_log_success(self, progress_log_service, mock_db, sample_progress_log):
        """Test successful progress log creation."""
        progress_data = ProgressLogCreate(
            user_id=1,
            exercise_id=1,
            workout_date=datetime.utcnow(),
            workout_type=WorkoutType.STRENGTH.value,
            weight=75.5,
            notes="Great progress!",
            sets=3,
            reps="10"
        )
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('app.models.progress_log.ProgressLog') as mock_progress:
            mock_progress.return_value = sample_progress_log
            
            result = progress_log_service.create_progress_log(mock_db, progress_data, trainer_id=1)
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            assert result.weight == 75.5
    
    def test_get_progress_log_by_id_success(self, progress_log_service, mock_db, sample_progress_log):
        """Test successful progress log retrieval by ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_progress_log
        
        result = progress_log_service.get_progress_log_by_id(mock_db, progress_log_id=1)
        
        assert result == sample_progress_log
        mock_db.query.assert_called_once()
    
    def test_get_progress_log_by_id_not_found(self, progress_log_service, mock_db):
        """Test progress log retrieval when log doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            progress_log_service.get_progress_log_by_id(mock_db, progress_log_id=999)
        
        assert exc_info.value.status_code == 404
        assert "Progress log not found" in str(exc_info.value.detail)
    
    def test_update_progress_log_success(self, progress_log_service, mock_db, sample_progress_log):
        """Test successful progress log update."""
        update_data = ProgressLogUpdate(
            weight=80.0,
            notes="Even better progress!"
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = sample_progress_log
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        result = progress_log_service.update_progress_log(mock_db, progress_log_id=1, progress_update=update_data, trainer_id=1)
        
        assert result.weight == 80.0
        assert result.notes == "Even better progress!"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_update_progress_log_unauthorized(self, progress_log_service, mock_db, sample_progress_log):
        """Test unauthorized progress log update attempt."""
        sample_progress_log.trainer_id = 2  # Different trainer
        mock_db.query.return_value.filter.return_value.first.return_value = sample_progress_log
        
        update_data = ProgressLogUpdate(weight=80.0)
        
        with pytest.raises(HTTPException) as exc_info:
            progress_log_service.update_progress_log(mock_db, progress_log_id=1, progress_update=update_data, trainer_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value.detail)
    
    def test_delete_progress_log_success(self, progress_log_service, mock_db, sample_progress_log):
        """Test successful progress log deletion."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_progress_log
        mock_db.delete = Mock()
        mock_db.commit = Mock()
        
        result = progress_log_service.delete_progress_log(mock_db, progress_log_id=1, trainer_id=1)
        
        assert result is True
        mock_db.delete.assert_called_once_with(sample_progress_log)
        mock_db.commit.assert_called_once()
    
    def test_delete_progress_log_unauthorized(self, progress_log_service, mock_db, sample_progress_log):
        """Test unauthorized progress log deletion attempt."""
        sample_progress_log.trainer_id = 2  # Different trainer
        mock_db.query.return_value.filter.return_value.first.return_value = sample_progress_log
        
        with pytest.raises(HTTPException) as exc_info:
            progress_log_service.delete_progress_log(mock_db, progress_log_id=1, trainer_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value.detail)
    
    def test_get_client_progress_logs(self, progress_log_service, mock_db):
        """Test getting progress logs for a client."""
        progress_logs = [Mock(spec=ProgressLog) for _ in range(5)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = progress_logs
        mock_db.query.return_value = mock_query
        
        result = progress_log_service.get_client_progress_logs(mock_db, user_id=1, skip=0, limit=10)
        
        assert len(result) == 5
        mock_db.query.assert_called_once()
    
    def test_get_progress_logs_by_type(self, progress_log_service, mock_db):
        """Test getting progress logs by type."""
        progress_logs = [Mock(spec=ProgressLog) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = progress_logs
        mock_db.query.return_value = mock_query
        
        result = progress_log_service.get_progress_logs_by_type(mock_db, user_id=1, progress_type=ProgressType.WEIGHT)
        
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_get_progress_logs_by_date_range(self, progress_log_service, mock_db):
        """Test getting progress logs by date range."""
        progress_logs = [Mock(spec=ProgressLog) for _ in range(4)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = progress_logs
        mock_db.query.return_value = mock_query
        
        start_date = datetime.utcnow().date() - timedelta(days=30)
        end_date = datetime.utcnow().date()
        
        result = progress_log_service.get_progress_logs_by_date_range(
            mock_db, 
            user_id=1, 
            start_date=start_date, 
            end_date=end_date
        )
        
        assert len(result) == 4
        mock_db.query.assert_called_once()
    
    def test_get_latest_progress_by_type(self, progress_log_service, mock_db, sample_progress_log):
        """Test getting latest progress log by type."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_progress_log
        mock_db.query.return_value = mock_query
        
        result = progress_log_service.get_latest_progress_by_type(mock_db, user_id=1, progress_type=ProgressType.WEIGHT)
        
        assert result == sample_progress_log
        mock_db.query.assert_called_once()
    
    def test_get_progress_summary(self, progress_log_service, mock_db):
        """Test getting progress summary for a client."""
        # Mock multiple queries for different progress types
        mock_queries = [Mock() for _ in range(4)]
        for mock_query in mock_queries:
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.first.return_value = Mock(spec=ProgressLog, value=75.0, recorded_date=datetime.utcnow().date())
        
        mock_db.query.side_effect = mock_queries
        
        result = progress_log_service.get_progress_summary(mock_db, user_id=1)
        
        assert "weight" in result
        assert "body_fat" in result
        assert "muscle_mass" in result
        assert "measurements" in result
    
    def test_calculate_progress_trend(self, progress_log_service, mock_db):
        """Test calculating progress trend."""
        # Create mock progress logs with different values
        progress_logs = []
        for i, value in enumerate([70.0, 72.0, 74.0, 75.0, 76.0]):
            log = Mock(spec=ProgressLog)
            log.value = value
            log.recorded_date = datetime.utcnow().date() - timedelta(days=30-i*7)
            progress_logs.append(log)
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = progress_logs
        mock_db.query.return_value = mock_query
        
        result = progress_log_service.calculate_progress_trend(
            mock_db, 
            user_id=1, 
            progress_type=ProgressType.WEIGHT
        )
        
        assert "trend" in result
        assert "change" in result
        assert "percentage_change" in result
        assert result["trend"] == "increasing"
    
    def test_get_progress_statistics(self, progress_log_service, mock_db):
        """Test getting progress statistics."""
        # Mock aggregation query results
        mock_result = Mock()
        mock_result.avg_value = 75.0
        mock_result.min_value = 70.0
        mock_result.max_value = 80.0
        mock_result.count = 10
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.one.return_value = mock_result
        mock_db.query.return_value = mock_query
        
        result = progress_log_service.get_progress_statistics(
            mock_db, 
            user_id=1, 
            progress_type=ProgressType.WEIGHT
        )
        
        assert result["average"] == 75.0
        assert result["minimum"] == 70.0
        assert result["maximum"] == 80.0
        assert result["count"] == 10
    
    def test_bulk_create_progress_logs(self, progress_log_service, mock_db):
        """Test bulk creation of progress logs."""
        progress_data_list = [
            ProgressLogCreate(
                user_id=1,
                exercise_id=1,
                workout_date=datetime.utcnow(),
                workout_type=WorkoutType.STRENGTH.value,
                weight=75.0,
                notes="Weight training session"
            ),
            ProgressLogCreate(
                user_id=1,
                exercise_id=2,
                workout_date=datetime.utcnow(),
                workout_type=WorkoutType.CARDIO.value,
                duration=1800,  # 30 minutes in seconds
                notes="Cardio session"
            )
        ]
        
        mock_db.add_all = Mock()
        mock_db.commit = Mock()
        
        with patch('app.models.progress_log.ProgressLog') as mock_progress:
            mock_progress.side_effect = [Mock(spec=ProgressLog), Mock(spec=ProgressLog)]
            
            result = progress_log_service.bulk_create_progress_logs(mock_db, progress_data_list)
            
            assert len(result) == 2
            mock_db.add_all.assert_called_once()
            mock_db.commit.assert_called_once()
    
    def test_export_progress_data(self, progress_log_service, mock_db):
        """Test exporting progress data."""
        progress_logs = [Mock(spec=ProgressLog) for _ in range(5)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = progress_logs
        mock_db.query.return_value = mock_query
        
        result = progress_log_service.export_progress_data(mock_db, user_id=1)
        
        assert len(result) == 5
        mock_db.query.assert_called_once()
    
    def test_get_progress_goals_comparison(self, progress_log_service, mock_db, sample_progress_log):
        """Test comparing progress with goals."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_progress_log
        mock_db.query.return_value = mock_query
        
        goals = {
            "weight": {"target": 70.0, "unit": "kg"},
            "body_fat": {"target": 12.0, "unit": "%"}
        }
        
        result = progress_log_service.get_progress_goals_comparison(mock_db, user_id=1, goals=goals)
        
        assert "weight" in result
        assert "progress_percentage" in result["weight"]
        assert "remaining" in result["weight"]
