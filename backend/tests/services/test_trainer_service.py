import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.trainer_service import trainer_service
from app.models.trainer import Trainer, TrainerCertification
from app.models.user import User, UserRole
from app.schemas.trainer import TrainerCreate, TrainerUpdate, TrainerCertificationCreate


class TestTrainerService:
    """Test suite for TrainerService."""
    
    def test_create_trainer_success(self, db: Session):
        """Test successful trainer creation."""
        # Create a user first
        user = User(
            email="trainer@example.com",
            username="trainer123",
            hashed_password="hashed_password",
            full_name="Test Trainer",
            role=UserRole.TRAINER,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Experienced fitness trainer",
            specializations=["strength_training", "weight_loss"],
            certifications=["NASM-CPT"],
            experience_years=5,
            hourly_rate=75.0,
            location="New York, NY"
        )
        
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        assert trainer is not None
        assert trainer.user_id == user.id
        assert trainer.bio == trainer_data.bio
        assert trainer.hourly_rate == trainer_data.hourly_rate
        assert trainer.experience_years == trainer_data.experience_years
    
    def test_create_trainer_duplicate_user(self, db: Session):
        """Test trainer creation with duplicate user ID."""
        # Create a user and trainer first
        user = User(
            email="duplicate@example.com",
            username="duplicate",
            hashed_password="hashed_password",
            full_name="Duplicate User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="First trainer",
            hourly_rate=50.0
        )
        trainer_service.create_trainer(db, trainer_data)
        
        # Try to create another trainer for same user
        duplicate_data = TrainerCreate(
            user_id=user.id,
            bio="Second trainer",
            hourly_rate=60.0
        )
        
        with pytest.raises(HTTPException) as exc_info:
            trainer_service.create_trainer(db, duplicate_data)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail).lower()
    
    def test_get_trainer_by_id_success(self, db: Session):
        """Test successful trainer retrieval by ID."""
        # Create user and trainer
        user = User(
            email="getbyid@example.com",
            username="getbyid",
            hashed_password="hashed_password",
            full_name="Get By ID User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Test trainer",
            hourly_rate=50.0
        )
        created_trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Retrieve trainer
        retrieved_trainer = trainer_service.get_trainer_by_id(db, created_trainer.id)
        
        assert retrieved_trainer is not None
        assert retrieved_trainer.id == created_trainer.id
        assert retrieved_trainer.bio == trainer_data.bio
    
    def test_get_trainer_by_id_not_found(self, db: Session):
        """Test trainer retrieval with non-existent ID."""
        result = trainer_service.get_trainer_by_id(db, 99999)
        
        assert result is None
    
    def test_get_trainer_by_user_id_success(self, db: Session):
        """Test successful trainer retrieval by user ID."""
        # Create user and trainer
        user = User(
            email="getbyuserid@example.com",
            username="getbyuserid",
            hashed_password="hashed_password",
            full_name="Get By User ID",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Test trainer",
            hourly_rate=50.0
        )
        created_trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Retrieve by user ID
        retrieved_trainer = trainer_service.get_trainer_by_user_id(db, user.id)
        
        assert retrieved_trainer is not None
        assert retrieved_trainer.user_id == user.id
        assert retrieved_trainer.id == created_trainer.id
    
    def test_get_trainer_by_user_id_not_found(self, db: Session):
        """Test trainer retrieval with non-existent user ID."""
        result = trainer_service.get_trainer_by_user_id(db, 99999)
        
        assert result is None
    
    def test_update_trainer_success(self, db: Session):
        """Test successful trainer update."""
        # Create user and trainer
        user = User(
            email="update@example.com",
            username="update",
            hashed_password="hashed_password",
            full_name="Update User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Original bio",
            hourly_rate=50.0,
            experience_years=3
        )
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Update trainer
        update_data = TrainerUpdate(
            bio="Updated bio",
            hourly_rate=75.0,
            experience_years=5,
            specializations=["strength", "cardio"]
        )
        
        updated_trainer = trainer_service.update_trainer(db, trainer.id, update_data)
        
        assert updated_trainer is not None
        assert updated_trainer.bio == "Updated bio"
        assert updated_trainer.hourly_rate == 75.0
        assert updated_trainer.experience_years == 5
    
    def test_update_trainer_not_found(self, db: Session):
        """Test trainer update with non-existent ID."""
        update_data = TrainerUpdate(bio="Updated bio")
        
        result = trainer_service.update_trainer(db, 99999, update_data)
        
        assert result is None
    
    def test_delete_trainer_success(self, db: Session):
        """Test successful trainer deletion."""
        # Create user and trainer
        user = User(
            email="delete@example.com",
            username="delete",
            hashed_password="hashed_password",
            full_name="Delete User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="To be deleted",
            hourly_rate=50.0
        )
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Delete trainer
        result = trainer_service.delete_trainer(db, trainer.id)
        
        assert result is True
        
        # Verify deletion
        deleted_trainer = trainer_service.get_trainer_by_id(db, trainer.id)
        assert deleted_trainer is None
    
    def test_delete_trainer_not_found(self, db: Session):
        """Test trainer deletion with non-existent ID."""
        result = trainer_service.delete_trainer(db, 99999)
        
        assert result is False
    
    def test_get_all_trainers(self, db: Session):
        """Test getting all trainers."""
        # Create multiple trainers
        for i in range(3):
            user = User(
                email=f"trainer{i}@example.com",
                username=f"trainer{i}",
                hashed_password="hashed_password",
                full_name=f"Trainer {i}",
                role=UserRole.TRAINER
            )
            db.add(user)
            db.commit()
            
            trainer_data = TrainerCreate(
                user_id=user.id,
                bio=f"Trainer {i} bio",
                hourly_rate=50.0 + i * 10
            )
            trainer_service.create_trainer(db, trainer_data)
        
        # Get all trainers
        trainers = trainer_service.get_all_trainers(db, skip=0, limit=10)
        
        assert len(trainers) >= 3
        assert all(isinstance(trainer, Trainer) for trainer in trainers)
    
    def test_get_all_trainers_with_pagination(self, db: Session):
        """Test trainer list with pagination."""
        # Create multiple trainers
        for i in range(5):
            user = User(
                email=f"paginate{i}@example.com",
                username=f"paginate{i}",
                hashed_password="hashed_password",
                full_name=f"Paginate {i}",
                role=UserRole.TRAINER
            )
            db.add(user)
            db.commit()
            
            trainer_data = TrainerCreate(
                user_id=user.id,
                bio=f"Paginate {i} bio",
                hourly_rate=50.0
            )
            trainer_service.create_trainer(db, trainer_data)
        
        # Test pagination
        page1 = trainer_service.get_all_trainers(db, skip=0, limit=2)
        page2 = trainer_service.get_all_trainers(db, skip=2, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id  # Different trainers
    
    def test_search_trainers_by_specialization(self, db: Session):
        """Test trainer search by specialization."""
        # Create trainers with different specializations
        specializations = [
            ["strength_training"],
            ["cardio", "weight_loss"],
            ["yoga", "flexibility"]
        ]
        
        for i, specs in enumerate(specializations):
            user = User(
                email=f"spec{i}@example.com",
                username=f"spec{i}",
                hashed_password="hashed_password",
                full_name=f"Spec {i}",
                role=UserRole.TRAINER
            )
            db.add(user)
            db.commit()
            
            trainer_data = TrainerCreate(
                user_id=user.id,
                bio=f"Specialist {i}",
                hourly_rate=50.0,
                specializations=specs
            )
            trainer_service.create_trainer(db, trainer_data)
        
        # Search by specialization
        results = trainer_service.search_trainers(
            db, specialization="strength_training", location=None, min_experience=None
        )
        
        # Should find at least one trainer with strength_training
        assert len(results) >= 1
    
    def test_get_trainer_stats(self, db: Session):
        """Test trainer statistics calculation."""
        # Create user and trainer
        user = User(
            email="stats@example.com",
            username="stats",
            hashed_password="hashed_password",
            full_name="Stats User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Stats trainer",
            hourly_rate=50.0
        )
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Get stats
        stats = trainer_service.get_trainer_stats(db, trainer.id)
        
        assert stats is not None
        assert hasattr(stats, 'total_sessions')
        assert hasattr(stats, 'revenue_this_month')
        assert hasattr(stats, 'active_clients')
    
    def test_get_trainer_dashboard(self, db: Session):
        """Test trainer dashboard data retrieval."""
        # Create user and trainer
        user = User(
            email="dashboard@example.com",
            username="dashboard",
            hashed_password="hashed_password",
            full_name="Dashboard User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Dashboard trainer",
            hourly_rate=50.0
        )
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Get dashboard
        dashboard = trainer_service.get_trainer_dashboard(db, trainer.id)
        
        assert dashboard is not None
        assert hasattr(dashboard, 'total_clients')
        assert hasattr(dashboard, 'active_programs')
        assert hasattr(dashboard, 'upcoming_sessions')


class TestTrainerCertificationService:
    """Test trainer certification management."""
    
    def test_add_certification_success(self, db: Session):
        """Test successful certification addition."""
        # Create user and trainer
        user = User(
            email="cert@example.com",
            username="cert",
            hashed_password="hashed_password",
            full_name="Cert User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Certified trainer",
            hourly_rate=50.0
        )
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Add certification
        cert_data = TrainerCertificationCreate(
            trainer_id=trainer.id,
            name="NASM-CPT",
            issuing_organization="National Academy of Sports Medicine",
            issue_date=datetime(2023, 1, 15),
            expiry_date=datetime(2025, 1, 15),
            certificate_number="CPT123456"
        )
        
        certification = trainer_service.add_certification(db, trainer.id, cert_data)
        
        assert certification is not None
        assert certification.trainer_id == trainer.id
        assert certification.name == "NASM-CPT"
        assert certification.certificate_number == "CPT123456"
    
    def test_get_trainer_certifications(self, db: Session):
        """Test getting trainer certifications."""
        # Create user and trainer
        user = User(
            email="getcerts@example.com",
            username="getcerts",
            hashed_password="hashed_password",
            full_name="Get Certs User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Multi-certified trainer",
            hourly_rate=50.0
        )
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Add multiple certifications
        cert_names = ["NASM-CPT", "ACSM-EP", "NSCA-CSCS"]
        for cert_name in cert_names:
            cert_data = TrainerCertificationCreate(
                trainer_id=trainer.id,
                name=cert_name,
                issuing_organization="Test Org",
                issue_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=365)).date()
            )
            trainer_service.add_certification(db, trainer.id, cert_data)
        
        # Get certifications
        certifications = trainer_service.get_trainer_certifications(db, trainer.id)
        
        assert len(certifications) == 3
        cert_names_returned = [cert.name for cert in certifications]
        assert all(name in cert_names_returned for name in cert_names)


class TestTrainerServiceValidation:
    """Test trainer service validation and edge cases."""
    
    def test_create_trainer_invalid_hourly_rate(self, db: Session):
        """Test trainer creation with invalid hourly rate."""
        user = User(
            email="invalidrate@example.com",
            username="invalidrate",
            hashed_password="hashed_password",
            full_name="Invalid Rate User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        # Test negative rate (should be handled by validation)
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Invalid rate trainer",
            hourly_rate=-50.0
        )
        
        # Depending on implementation, this might raise an exception
        # or be handled gracefully
        try:
            trainer = trainer_service.create_trainer(db, trainer_data)
            # If creation succeeds, rate should be handled somehow
            assert trainer.hourly_rate >= 0
        except (HTTPException, ValueError):
            # Expected if validation rejects negative rates
            pass
    
    def test_update_trainer_partial_data(self, db: Session):
        """Test trainer update with partial data."""
        # Create user and trainer
        user = User(
            email="partial@example.com",
            username="partial",
            hashed_password="hashed_password",
            full_name="Partial User",
            role=UserRole.TRAINER
        )
        db.add(user)
        db.commit()
        
        trainer_data = TrainerCreate(
            user_id=user.id,
            bio="Original bio",
            hourly_rate=50.0,
            experience_years=3
        )
        trainer = trainer_service.create_trainer(db, trainer_data)
        
        # Update only bio
        update_data = TrainerUpdate(bio="Updated bio only")
        updated_trainer = trainer_service.update_trainer(db, trainer.id, update_data)
        
        assert updated_trainer.bio == "Updated bio only"
        assert updated_trainer.hourly_rate == 50.0  # Should remain unchanged
        assert updated_trainer.experience_years == 3  # Should remain unchanged
    
    def test_trainer_search_no_results(self, db: Session):
        """Test trainer search with no matching results."""
        results = trainer_service.search_trainers(
            db, 
            specialization="nonexistent_specialization",
            location="Nonexistent City",
            min_experience=100
        )
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_trainer_service_database_error_handling(self, db: Session):
        """Test service behavior with database errors."""
        # Create trainer data with non-existent user_id
        trainer_data = TrainerCreate(
            user_id=99999,  # Non-existent user
            bio="Error test trainer",
            hourly_rate=50.0
        )
        
        # This should raise an exception due to foreign key constraint
        with pytest.raises((HTTPException, Exception)):
            trainer_service.create_trainer(db, trainer_data)
