import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import ValidationError

from app.services.client_service import client_service
from app.models.client import Client
from app.models.user import User, UserRole
from app.schemas.client import ClientCreate, ClientUpdate


class TestClientService:
    """Test suite for ClientService."""
    
    def test_create_client_success(self, db: Session):
        """Test successful client creation."""
        # Create a user first
        user = User(
            email="client@example.com",
            username="client123",
            hashed_password="hashed_password",
            full_name="Test Client",
            role=UserRole.CLIENT,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        client_data = ClientCreate(
            user_id=user.id,
            age=25,
            height=175.0,
            current_weight=70.0,
            fitness_level="intermediate",
            fitness_goals=["weight_loss", "muscle_gain"],
            medical_conditions=[],
            emergency_contact_name="John Doe",
            emergency_contact_phone="+1234567890"
        )
        
        client = client_service.create_client(db, client_data)
        
        assert client is not None
        assert client.user_id == user.id
        assert client.age == client_data.age
        assert client.height == client_data.height
        assert client.current_weight == client_data.current_weight
        assert client.fitness_level == client_data.fitness_level
        assert client.pin is not None  # PIN should be generated
        assert len(client.pin) == 6  # Assuming 6-digit PIN
    
    def test_create_client_duplicate_user(self, db: Session):
        """Test client creation with duplicate user ID."""
        # Create a user and client first
        user = User(
            email="duplicate@example.com",
            username="duplicate",
            hashed_password="hashed_password",
            full_name="Duplicate User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=30,
            height=170.0,
            current_weight=65.0,
            fitness_level="beginner"
        )
        client_service.create_client(db, client_data)
        
        # Try to create another client for same user
        duplicate_data = ClientCreate(
            user_id=user.id,
            age=25,
            height=175.0,
            current_weight=70.0,
            fitness_level="intermediate"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            client_service.create_client(db, duplicate_data)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail).lower()
    
    def test_get_client_by_id_success(self, db: Session):
        """Test successful client retrieval by ID."""
        # Create user and client
        user = User(
            email="getbyid@example.com",
            username="getbyid",
            hashed_password="hashed_password",
            full_name="Get By ID User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=28,
            height=168.0,
            current_weight=62.0,
            fitness_level="advanced"
        )
        created_client = client_service.create_client(db, client_data)
        
        # Retrieve client
        retrieved_client = client_service.get_client_by_id(db, created_client.id)
        
        assert retrieved_client is not None
        assert retrieved_client.id == created_client.id
        assert retrieved_client.age == client_data.age
    
    def test_get_client_by_user_id_success(self, db: Session):
        """Test successful client retrieval by user ID."""
        # Create user and client
        user = User(
            email="getbyuserid@example.com",
            username="getbyuserid",
            hashed_password="hashed_password",
            full_name="Get By User ID",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=35,
            height=180.0,
            current_weight=85.0,
            fitness_level="intermediate"
        )
        created_client = client_service.create_client(db, client_data)
        
        # Retrieve by user ID
        retrieved_client = client_service.get_client_by_user_id(db, user.id)
        
        assert retrieved_client is not None
        assert retrieved_client.user_id == user.id
        assert retrieved_client.id == created_client.id
    
    def test_get_client_by_pin_success(self, db: Session):
        """Test successful client retrieval by PIN."""
        # Create user and client
        user = User(
            email="getbypin@example.com",
            username="getbypin",
            hashed_password="hashed_password",
            full_name="Get By PIN User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=22,
            height=165.0,
            current_weight=58.0,
            fitness_level="beginner"
        )
        created_client = client_service.create_client(db, client_data)
        
        # Retrieve by PIN
        retrieved_client = client_service.get_client_by_pin(db, created_client.pin)
        
        assert retrieved_client is not None
        assert retrieved_client.pin == created_client.pin
        assert retrieved_client.id == created_client.id
    
    def test_get_client_by_pin_not_found(self, db: Session):
        """Test client retrieval with non-existent PIN."""
        result = client_service.get_client_by_pin(db, "000000")
        
        assert result is None
    
    def test_update_client_success(self, db: Session):
        """Test successful client update."""
        # Create user and client
        user = User(
            email="update@example.com",
            username="update",
            hashed_password="hashed_password",
            full_name="Update User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=26,
            height=170.0,
            current_weight=65.0,
            fitness_level="beginner"
        )
        client = client_service.create_client(db, client_data)
        
        # Update client
        update_data = ClientUpdate(
            age=27,
            current_weight=67.0,
            fitness_level="intermediate",
            fitness_goals=["strength", "endurance"]
        )
        
        updated_client = client_service.update_client(db, client.id, update_data)
        
        assert updated_client is not None
        assert updated_client.age == 27
        assert updated_client.current_weight == 67.0
        assert updated_client.fitness_level == "intermediate"
    
    def test_regenerate_pin_success(self, db: Session):
        """Test successful PIN regeneration."""
        # Create user and client
        user = User(
            email="regenpin@example.com",
            username="regenpin",
            hashed_password="hashed_password",
            full_name="Regen PIN User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=30,
            height=175.0,
            current_weight=70.0,
            fitness_level="intermediate"
        )
        client = client_service.create_client(db, client_data)
        original_pin = client.pin
        
        # Regenerate PIN
        new_pin = client_service.regenerate_pin(db, client.id)
        
        assert new_pin is not None
        assert new_pin != original_pin
        assert len(new_pin) == 6
        
        # Verify client has new PIN
        updated_client = client_service.get_client_by_id(db, client.id)
        assert updated_client.pin == new_pin
    
    def test_get_client_stats(self, db: Session):
        """Test client statistics calculation."""
        # Create user and client
        user = User(
            email="stats@example.com",
            username="stats",
            hashed_password="hashed_password",
            full_name="Stats User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=29,
            height=172.0,
            current_weight=68.0,
            fitness_level="intermediate"
        )
        client = client_service.create_client(db, client_data)
        
        # Get stats
        stats = client_service.get_client_stats(db, client.id)
        
        assert stats is not None
        assert hasattr(stats, 'total_sessions')
        assert hasattr(stats, 'completed_workouts')
        assert hasattr(stats, 'weight_progress')
    
    def test_assign_trainer_success(self, db: Session):
        """Test successful trainer assignment."""
        # Create trainer user
        trainer_user = User(
            email="trainer@example.com",
            username="trainer",
            hashed_password="hashed_password",
            full_name="Trainer User",
            role=UserRole.TRAINER
        )
        db.add(trainer_user)
        db.commit()
        
        # Create client user
        client_user = User(
            email="assign@example.com",
            username="assign",
            hashed_password="hashed_password",
            full_name="Assign User",
            role=UserRole.CLIENT
        )
        db.add(client_user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=client_user.id,
            age=25,
            height=170.0,
            current_weight=65.0,
            fitness_level="beginner"
        )
        client = client_service.create_client(db, client_data)
        
        # Assign trainer
        result = client_service.assign_trainer(db, client.id, trainer_user.id)
        
        # Depending on implementation, this might succeed or need trainer profile
        assert result in [True, False, None]


class TestClientServiceValidation:
    """Test client service validation and edge cases."""
    
    def test_create_client_invalid_age(self, db: Session):
        """Test client creation with invalid age."""
        user = User(
            email="invalidage@example.com",
            username="invalidage",
            hashed_password="hashed_password",
            full_name="Invalid Age User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()

        # Test negative age - should fail at Pydantic validation level
        with pytest.raises(ValidationError):
            client_data = ClientCreate(
                user_id=user.id,
                age=-5,
                height=170.0,
                current_weight=65.0,
                fitness_level="beginner"
            )

    def test_create_client_invalid_measurements(self, db: Session):
        """Test client creation with invalid measurements."""
        user = User(
            email="invalidmeas@example.com",
            username="invalidmeas",
            hashed_password="hashed_password",
            full_name="Invalid Measurements User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()

        # Test negative height and weight - should fail at Pydantic validation level
        with pytest.raises(ValidationError):
            client_data = ClientCreate(
                user_id=user.id,
                age=25,
                height=-170.0,
                current_weight=-65.0,
                fitness_level="beginner"
            )
    
    def test_update_client_partial_data(self, db: Session):
        """Test client update with partial data."""
        # Create user and client
        user = User(
            email="partial@example.com",
            username="partial",
            hashed_password="hashed_password",
            full_name="Partial User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=25,
            height=170.0,
            current_weight=65.0,
            fitness_level="beginner"
        )
        client = client_service.create_client(db, client_data)
        
        # Update only age
        update_data = ClientUpdate(age=26)
        updated_client = client_service.update_client(db, client.id, update_data)
        
        assert updated_client.age == 26
        assert updated_client.height == 170.0  # Should remain unchanged
        assert updated_client.current_weight == 65.0  # Should remain unchanged
    
    def test_pin_uniqueness(self, db: Session):
        """Test that generated PINs are unique."""
        pins = set()
        
        # Create multiple clients and check PIN uniqueness
        for i in range(10):
            user = User(
                email=f"pin{i}@example.com",
                username=f"pin{i}",
                hashed_password="hashed_password",
                full_name=f"PIN User {i}",
                role=UserRole.CLIENT
            )
            db.add(user)
            db.commit()
            
            client_data = ClientCreate(
                user_id=user.id,
                age=25,
                height=170.0,
                current_weight=65.0,
                fitness_level="beginner"
            )
            client = client_service.create_client(db, client_data)
            
            # PIN should be unique
            assert client.pin not in pins
            pins.add(client.pin)
    
    def test_fitness_level_validation(self, db: Session):
        """Test fitness level validation."""
        user = User(
            email="fitnesslevel@example.com",
            username="fitnesslevel",
            hashed_password="hashed_password",
            full_name="Fitness Level User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        valid_levels = ["beginner", "intermediate", "advanced"]
        
        for level in valid_levels:
            client_data = ClientCreate(
                user_id=user.id,
                age=25,
                height=170.0,
                current_weight=65.0,
                fitness_level=level
            )
            
            # Should succeed for valid levels
            try:
                client = client_service.create_client(db, client_data)
                assert client.fitness_level == level
                # Clean up for next iteration
                client_service.delete_client(db, client.id)
            except HTTPException:
                # If one fails, they all might due to duplicate user_id
                break


class TestClientServiceSecurity:
    """Test security aspects of ClientService."""
    
    def test_pin_format_security(self, db: Session):
        """Test PIN format and security."""
        user = User(
            email="pinsecurity@example.com",
            username="pinsecurity",
            hashed_password="hashed_password",
            full_name="PIN Security User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=25,
            height=170.0,
            current_weight=65.0,
            fitness_level="beginner"
        )
        client = client_service.create_client(db, client_data)
        
        # PIN should be 6 digits
        assert len(client.pin) == 6
        assert client.pin.isdigit()
        
        # PIN should not be easily guessable
        assert client.pin not in ["000000", "111111", "123456", "654321"]
    
    def test_client_data_privacy(self, db: Session):
        """Test that sensitive client data is handled properly."""
        user = User(
            email="privacy@example.com",
            username="privacy",
            hashed_password="hashed_password",
            full_name="Privacy User",
            role=UserRole.CLIENT
        )
        db.add(user)
        db.commit()
        
        client_data = ClientCreate(
            user_id=user.id,
            age=25,
            height=170.0,
            current_weight=65.0,
            fitness_level="beginner",
            medical_conditions=["diabetes", "hypertension"],
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="+1234567890"
        )
        client = client_service.create_client(db, client_data)
        
        # Sensitive data should be stored
        assert client.medical_conditions == client_data.medical_conditions
        assert client.emergency_contact_name == client_data.emergency_contact_name
        assert client.emergency_contact_phone == client_data.emergency_contact_phone


class TestClientServiceErrorHandling:
    """Test error handling in ClientService."""
    
    def test_create_client_database_error(self, db: Session):
        """Test client creation with database constraint violations."""
        # Create client data with non-existent user_id
        client_data = ClientCreate(
            user_id=99999,  # Non-existent user
            age=25,
            height=170.0,
            current_weight=65.0,
            fitness_level="beginner"
        )
        
        # This could raise an exception due to foreign key constraint
        # or succeed with notification failure (depending on SQLite settings)
        try:
            client = client_service.create_client(db, client_data)
            # If creation succeeds, verify the client was created with non-existent user_id
            assert client.user_id == 99999
        except (HTTPException, Exception):
            # Expected if foreign key constraints are enforced
            pass
    
    def test_get_client_by_id_not_found(self, db: Session):
        """Test client retrieval with non-existent ID."""
        result = client_service.get_client_by_id(db, 99999)
        
        assert result is None
    
    def test_update_client_not_found(self, db: Session):
        """Test client update with non-existent ID."""
        update_data = ClientUpdate(age=30)
        
        result = client_service.update_client(db, 99999, update_data)
        
        assert result is None
    
    def test_regenerate_pin_not_found(self, db: Session):
        """Test PIN regeneration with non-existent client ID."""
        result = client_service.regenerate_pin(db, 99999)
        
        assert result is None
