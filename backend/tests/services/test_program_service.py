import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.program_service import ProgramService
from app.models.program import Program, ProgramStatus
from app.schemas.program import ProgramCreate, ProgramUpdate


@pytest.fixture
def program_service():
    """Create ProgramService instance for testing."""
    return ProgramService()


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def sample_program():
    """Create a sample program for testing."""
    return Program(
        id=1,
        name="Test Program",
        description="Test Description",
        trainer_id=1,
        duration_weeks=12,
        difficulty_level="Intermediate",
        goals=["Weight Loss", "Muscle Building"],
        target_audience="Beginners",
        status=ProgramStatus.ACTIVE,
        price=99.99,
        max_participants=20,
        is_public=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestProgramService:
    """Test suite for ProgramService."""
    
    def test_create_program_success(self, program_service, mock_db, sample_program):
        """Test successful program creation."""
        program_data = ProgramCreate(
            name="Test Program",
            description="Test Description",
            duration_weeks=12,
            difficulty_level="Intermediate",
            goals=["Weight Loss", "Muscle Building"],
            target_audience="Beginners",
            price=99.99,
            max_participants=20,
            is_public=True
        )
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('app.models.program.Program') as mock_program:
            mock_program.return_value = sample_program
            
            result = program_service.create_program(mock_db, program_data, trainer_id=1)
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            assert result.name == "Test Program"
    
    def test_get_program_by_id_success(self, program_service, mock_db, sample_program):
        """Test successful program retrieval by ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        
        result = program_service.get_program_by_id(mock_db, program_id=1)
        
        assert result == sample_program
        mock_db.query.assert_called_once()
    
    def test_get_program_by_id_not_found(self, program_service, mock_db):
        """Test program retrieval when program doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            program_service.get_program_by_id(mock_db, program_id=999)
        
        assert exc_info.value.status_code == 404
        assert "Program not found" in str(exc_info.value.detail)
    
    def test_update_program_success(self, program_service, mock_db, sample_program):
        """Test successful program update."""
        update_data = ProgramUpdate(
            name="Updated Program",
            description="Updated Description",
            price=149.99
        )
        
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        result = program_service.update_program(mock_db, program_id=1, program_update=update_data, trainer_id=1)
        
        assert result.name == "Updated Program"
        assert result.description == "Updated Description"
        assert result.price == 149.99
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_update_program_unauthorized(self, program_service, mock_db, sample_program):
        """Test unauthorized program update attempt."""
        sample_program.trainer_id = 2  # Different trainer
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        
        update_data = ProgramUpdate(name="Unauthorized Update")
        
        with pytest.raises(HTTPException) as exc_info:
            program_service.update_program(mock_db, program_id=1, program_update=update_data, trainer_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value.detail)
    
    def test_delete_program_success(self, program_service, mock_db, sample_program):
        """Test successful program deletion."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        mock_db.delete = Mock()
        mock_db.commit = Mock()
        
        result = program_service.delete_program(mock_db, program_id=1, trainer_id=1)
        
        assert result is True
        mock_db.delete.assert_called_once_with(sample_program)
        mock_db.commit.assert_called_once()
    
    def test_delete_program_unauthorized(self, program_service, mock_db, sample_program):
        """Test unauthorized program deletion attempt."""
        sample_program.trainer_id = 2  # Different trainer
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        
        with pytest.raises(HTTPException) as exc_info:
            program_service.delete_program(mock_db, program_id=1, trainer_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value.detail)
    
    def test_get_programs_by_trainer(self, program_service, mock_db):
        """Test getting programs by trainer."""
        programs = [Mock(spec=Program) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query
        
        result = program_service.get_programs_by_trainer(mock_db, trainer_id=1, skip=0, limit=10)
        
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_get_public_programs(self, program_service, mock_db):
        """Test getting public programs."""
        programs = [Mock(spec=Program) for _ in range(5)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query
        
        result = program_service.get_public_programs(mock_db, skip=0, limit=10)
        
        assert len(result) == 5
        mock_db.query.assert_called_once()
    
    def test_search_programs_by_name(self, program_service, mock_db):
        """Test searching programs by name."""
        programs = [Mock(spec=Program) for _ in range(2)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query
        
        result = program_service.search_programs_by_name(mock_db, search_term="fitness")
        
        assert len(result) == 2
        mock_db.query.assert_called_once()
    
    def test_get_programs_by_difficulty(self, program_service, mock_db):
        """Test getting programs by difficulty level."""
        programs = [Mock(spec=Program) for _ in range(4)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query
        
        result = program_service.get_programs_by_difficulty(mock_db, difficulty_level="Beginner")
        
        assert len(result) == 4
        mock_db.query.assert_called_once()
    
    def test_activate_program_success(self, program_service, mock_db, sample_program):
        """Test successful program activation."""
        sample_program.status = ProgramStatus.DRAFT
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        mock_db.commit = Mock()
        
        result = program_service.activate_program(mock_db, program_id=1, trainer_id=1)
        
        assert result.status == ProgramStatus.ACTIVE
        mock_db.commit.assert_called_once()
    
    def test_deactivate_program_success(self, program_service, mock_db, sample_program):
        """Test successful program deactivation."""
        sample_program.status = ProgramStatus.ACTIVE
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        mock_db.commit = Mock()
        
        result = program_service.deactivate_program(mock_db, program_id=1, trainer_id=1)
        
        assert result.status == ProgramStatus.INACTIVE
        mock_db.commit.assert_called_once()
    
    def test_get_program_participants_count(self, program_service, mock_db):
        """Test getting program participants count."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 15
        mock_db.query.return_value = mock_query
        
        result = program_service.get_program_participants_count(mock_db, program_id=1)
        
        assert result == 15
        mock_db.query.assert_called_once()
    
    def test_is_program_full(self, program_service, mock_db, sample_program):
        """Test checking if program is full."""
        sample_program.max_participants = 20
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        
        with patch.object(program_service, 'get_program_participants_count') as mock_count:
            mock_count.return_value = 20
            
            result = program_service.is_program_full(mock_db, program_id=1)
            
            assert result is True
    
    def test_is_program_not_full(self, program_service, mock_db, sample_program):
        """Test checking if program is not full."""
        sample_program.max_participants = 20
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        
        with patch.object(program_service, 'get_program_participants_count') as mock_count:
            mock_count.return_value = 15
            
            result = program_service.is_program_full(mock_db, program_id=1)
            
            assert result is False
    
    def test_get_programs_by_price_range(self, program_service, mock_db):
        """Test getting programs by price range."""
        programs = [Mock(spec=Program) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query
        
        result = program_service.get_programs_by_price_range(mock_db, min_price=50.0, max_price=150.0)
        
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_get_programs_by_duration(self, program_service, mock_db):
        """Test getting programs by duration."""
        programs = [Mock(spec=Program) for _ in range(2)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query
        
        result = program_service.get_programs_by_duration(mock_db, duration_weeks=12)
        
        assert len(result) == 2
        mock_db.query.assert_called_once()
    
    def test_get_program_stats(self, program_service, mock_db):
        """Test getting program statistics."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10
        mock_db.query.return_value = mock_query
        
        result = program_service.get_program_stats(mock_db, trainer_id=1)
        
        assert "total_programs" in result
        assert "active_programs" in result
        assert "draft_programs" in result
        assert "inactive_programs" in result
    
    def test_duplicate_program_success(self, program_service, mock_db, sample_program):
        """Test successful program duplication."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        result = program_service.duplicate_program(mock_db, program_id=1, trainer_id=1, new_name="Duplicated Program")
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_archive_program_success(self, program_service, mock_db, sample_program):
        """Test successful program archiving."""
        sample_program.status = ProgramStatus.ACTIVE
        mock_db.query.return_value.filter.return_value.first.return_value = sample_program
        mock_db.commit = Mock()
        
        result = program_service.archive_program(mock_db, program_id=1, trainer_id=1)
        
        assert result.status == ProgramStatus.ARCHIVED
        mock_db.commit.assert_called_once()
