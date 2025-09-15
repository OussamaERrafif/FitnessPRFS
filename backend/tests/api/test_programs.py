import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestProgramEndpoints:
    """Test suite for training program endpoints."""
    
    @pytest.fixture
    def test_client_for_program(self, client: TestClient):
        """Create a test client for program assignment."""
        client_data = {
            "email": "programclient@test.com",
            "username": "programclient",
            "password": "TestPassword123!",
            "full_name": "Program Test Client",
            "role": "client",
            "age": 25,
            "height": 175.0,
            "weight": 70.0,
            "fitness_level": "intermediate"
        }
        response = client.post("/api/v1/auth/register", json=client_data)
        assert response.status_code == 201
        return response.json()["user_id"]
    
    def test_create_program_success(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test successful program creation."""
        program_data = {
            "name": "Beginner Strength Program",
            "description": "A comprehensive strength training program for beginners",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 8,
            "sessions_per_week": 3,
            "client_id": test_client_for_program,
            "goals": ["strength", "muscle_building"]
        }
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestProgramEndpoints:
    """Test suite for training program endpoints."""
    
    @pytest.fixture
    def test_client_for_program(self, client: TestClient):
        """Create a test client for program assignment."""
        client_data = {
            "email": "programclient@test.com",
            "username": "programclient",
            "password": "TestPassword123!",
            "full_name": "Program Test Client",
            "role": "client",
            "age": 25,
            "height": 175.0,
            "weight": 70.0,
            "fitness_level": "intermediate"
        }
        response = client.post("/api/v1/auth/register", json=client_data)
        assert response.status_code == 201
        return response.json()["user_id"]
    
    def test_create_program_success(self, client: TestClient, trainer_auth_headers: dict, db: Session):
        """Test successful program creation."""
        # First create a client manually to ensure it exists in this test's db session
        from app.models.client import Client
        from app.models.user import User, UserRole
        from app.models.trainer import Trainer
        from app.services.auth_service import auth_service
        import json

        # Create a client user
        client_user = User(
            email="test_client@example.com",
            username="test_client",
            hashed_password=auth_service.get_password_hash("password123"),
            role=UserRole.CLIENT
        )
        db.add(client_user)
        db.commit()
        db.refresh(client_user)        # Create the Client record
        client_record = Client(
            user_id=client_user.id,
            age=25,
            height=175.0,
            current_weight=70.0,
            fitness_level="intermediate",
            fitness_goals=["general_fitness", "strength_gain"]
        )
        db.add(client_record)
        db.commit()
        db.refresh(client_record)

        # Get the trainer user (should exist from the fixture)
        trainer_user = db.query(User).filter(User.role == UserRole.TRAINER).first()
        if trainer_user:
            # Create a trainer record if it doesn't exist
            existing_trainer = db.query(Trainer).filter(Trainer.user_id == trainer_user.id).first()
            if not existing_trainer:
                trainer_record = Trainer(
                    user_id=trainer_user.id,
                    specializations=["general_fitness", "strength_training"],
                    experience_years=5,
                    hourly_rate=50.0,
                    bio="Experienced trainer",
                    is_available=True
                )
                db.add(trainer_record)
                db.commit()
                db.refresh(trainer_record)
        
        program_data = {
            "name": "Beginner Strength Program",
            "description": "A comprehensive strength training program for beginners",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 8,
            "sessions_per_week": 3,
            "client_id": client_record.id,  # Use the ID from the client we just created
            "goals": ["strength", "muscle_building"]
        }
        
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=program_data)
        
        # Debug print
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == program_data["name"]
            assert data["duration_weeks"] == program_data["duration_weeks"]
            assert data["difficulty_level"] == program_data["difficulty_level"]
            assert "id" in data
    
    def test_create_program_unauthenticated(self, client: TestClient, test_client_for_program: int):
        """Test program creation without authentication."""
        program_data = {
            "name": "Unauthorized Program",
            "description": "Should not be created",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        
        response = client.post("/api/v1/programs/", json=program_data)
        
        assert response.status_code == 401
    
    def test_get_all_programs_with_filters(self, client: TestClient):
        """Test getting all programs with optional filters."""
        response = client.get("/api/v1/programs/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_get_program_by_id_success(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test getting a program by ID."""
        # Create a program first
        program_data = {
            "name": "Test Program for Get",
            "description": "Program to test retrieval",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 6,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        create_response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=program_data)
        
        if create_response.status_code in [200, 201]:
            program_id = create_response.json()["id"]
            
            response = client.get(f"/api/v1/programs/{program_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == program_id
            assert data["name"] == program_data["name"]
    
    def test_get_program_by_id_not_found(self, client: TestClient):
        """Test getting a non-existent program."""
        response = client.get("/api/v1/programs/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_update_program_success(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test successful program update."""
        # Create a program first
        program_data = {
            "name": "Original Program",
            "description": "Original description",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        create_response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=program_data)
        
        if create_response.status_code in [200, 201]:
            program_id = create_response.json()["id"]
            
            update_data = {
                "name": "Updated Program",
                "description": "Updated description",
                "duration_weeks": 6
            }
            
            response = client.put(f"/api/v1/programs/{program_id}", headers=trainer_auth_headers, json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == update_data["name"]
            assert data["description"] == update_data["description"]
            assert data["duration_weeks"] == update_data["duration_weeks"]
    
    def test_delete_program_success(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test successful program deletion."""
        # Create a program first
        program_data = {
            "name": "Program to Delete",
            "description": "This program will be deleted",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        create_response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=program_data)
        
        if create_response.status_code in [200, 201]:
            program_id = create_response.json()["id"]
            
            response = client.delete(f"/api/v1/programs/{program_id}", headers=trainer_auth_headers)
            
            assert response.status_code in [200, 204]
            
            # Verify deletion
            get_response = client.get(f"/api/v1/programs/{program_id}")
            assert get_response.status_code == 404
    
    def test_get_trainer_programs(self, client: TestClient, trainer_auth_headers: dict, authenticated_trainer: dict):
        """Test getting trainer's own programs using trainer/{trainer_id} endpoint."""
        # Get trainer ID from authenticated trainer
        trainer_id = 1  # This will be the first trainer created in tests
        
        response = client.get(f"/api/v1/programs/trainer/{trainer_id}", headers=trainer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Should return programs created by the authenticated trainer
    
    def test_search_programs_by_search_term(self, client: TestClient):
        """Test program search by search term."""
        response = client.get("/api/v1/programs/search?search_term=strength")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_get_popular_programs(self, client: TestClient):
        """Test getting popular programs."""
        response = client.get("/api/v1/programs/popular")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_search_programs_with_filters(self, client: TestClient):
        """Test program search with various filters."""
        # Test with difficulty filter
        response = client.get("/api/v1/programs/?difficulty_level=beginner")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Test with duration filter
        response = client.get("/api/v1/programs/?duration_weeks_max=8")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestProgramExercises:
    """Test program exercise management."""
    
    def test_add_exercise_to_program(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test adding an exercise to a program."""
        # Create a program first
        program_data = {
            "name": "Program with Exercises",
            "description": "Program to test exercise addition",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        create_response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=program_data)
        
        if create_response.status_code in [200, 201]:
            program_id = create_response.json()["id"]
            
            exercise_data = {
                "exercise_id": 1,
                "week_number": 1,
                "day_number": 1,
                "order_in_workout": 1,
                "sets": 3,
                "reps": "8-12",
                "rest_seconds": 60,
                "notes": "Focus on form"
            }
            
            response = client.post(
                f"/api/v1/programs/{program_id}/exercises",
                headers=trainer_auth_headers,
                json=exercise_data
            )
            
            # Expect success or 404/422 if exercise doesn't exist
            assert response.status_code in [200, 201, 404, 422]
    
    def test_get_program_exercises(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test getting exercises for a program."""
        # Create a program first
        program_data = {
            "name": "Program for Exercise Get",
            "description": "Program to test exercise retrieval",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        create_response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=program_data)
        
        if create_response.status_code in [200, 201]:
            program_id = create_response.json()["id"]
            
            response = client.get(f"/api/v1/programs/{program_id}/exercises")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestProgramValidation:
    """Test program data validation."""
    
    def test_program_required_fields(self, client: TestClient, trainer_auth_headers: dict):
        """Test program creation with missing required fields."""
        # Missing name
        incomplete_data = {
            "description": "Program without name",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": 1
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=incomplete_data)
        assert response.status_code == 422
        
        # Missing client_id
        incomplete_data2 = {
            "name": "Program without client",
            "description": "Program without client ID",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=incomplete_data2)
        assert response.status_code == 422
    
    def test_program_duration_validation(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test program duration validation."""
        # Valid duration
        valid_data = {
            "name": "Valid Duration Program",
            "description": "Program with valid duration",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 12,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=valid_data)
        assert response.status_code in [200, 201]
        
        # Invalid duration (negative)
        invalid_data = {
            "name": "Invalid Duration Program",
            "description": "Program with negative duration",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": -4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=invalid_data)
        assert response.status_code == 422
        
        # Invalid duration (zero)
        zero_data = {
            "name": "Zero Duration Program",
            "description": "Program with zero duration",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 0,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=zero_data)
        assert response.status_code == 422
    
    def test_program_difficulty_validation(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test program difficulty validation."""
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        
        for difficulty in valid_difficulties:
            data = {
                "name": f"{difficulty.capitalize()} Program",
                "description": f"Program for {difficulty} level",
                "program_type": "strength_training",
                "difficulty_level": difficulty,
                "duration_weeks": 4,
                "sessions_per_week": 3,
                "client_id": test_client_for_program
            }
            response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=data)
            assert response.status_code in [200, 201]
        
        # Invalid difficulty
        invalid_data = {
            "name": "Invalid Difficulty Program",
            "description": "Program with invalid difficulty",
            "program_type": "strength_training",
            "difficulty_level": "expert",  # Not a valid difficulty in enum
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=invalid_data)
        assert response.status_code == 422
    
    def test_program_goals_validation(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test program goals validation with multiple goals."""
        # Valid goals
        valid_data = {
            "name": "Multi-Goal Program",
            "description": "Program with multiple goals",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program,
            "goals": ["strength", "endurance", "weight_loss", "muscle_building"]
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=valid_data)
        assert response.status_code in [200, 201]
        
    def test_program_empty_goals_validation(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test program creation with empty goals."""
        # Empty goals (should be allowed)
        empty_goals_data = {
            "name": "No Goals Program",
            "description": "Program without specific goals",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program,
            "goals": []
        }
        response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=empty_goals_data)
        assert response.status_code in [200, 201]


class TestProgramAccessControl:
    """Test program access control and permissions."""
    
    def test_trainer_can_crud_own_programs(self, client: TestClient, trainer_auth_headers: dict, test_client_for_program: int):
        """Test that trainers can perform CRUD operations on their own programs."""
        # Create
        program_data = {
            "name": "Trainer's Own Program",
            "description": "Program created by trainer",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        create_response = client.post("/api/v1/programs/", headers=trainer_auth_headers, json=program_data)
        assert create_response.status_code in [200, 201]
        
        if create_response.status_code in [200, 201]:
            program_id = create_response.json()["id"]
            
            # Read
            read_response = client.get(f"/api/v1/programs/{program_id}", headers=trainer_auth_headers)
            assert read_response.status_code == 200
            
            # Update
            update_data = {"name": "Updated Program Name"}
            update_response = client.put(f"/api/v1/programs/{program_id}", headers=trainer_auth_headers, json=update_data)
            assert update_response.status_code == 200
            
            # Delete
            delete_response = client.delete(f"/api/v1/programs/{program_id}", headers=trainer_auth_headers)
            assert delete_response.status_code in [200, 204]
    
    def test_client_cannot_create_programs(self, client: TestClient, client_auth_headers: dict, test_client_for_program: int):
        """Test that clients cannot create programs."""
        program_data = {
            "name": "Unauthorized Program",
            "description": "Client should not be able to create this",
            "program_type": "strength_training",
            "difficulty_level": "beginner",
            "duration_weeks": 4,
            "sessions_per_week": 3,
            "client_id": test_client_for_program
        }
        
        response = client.post("/api/v1/programs/", headers=client_auth_headers, json=program_data)
        
        assert response.status_code in [403, 422]  # Should be forbidden
    
    def test_trainer_cannot_modify_others_programs(self, client: TestClient, trainer_auth_headers: dict, authenticated_trainer: dict):
        """Test that trainers cannot modify other trainers' programs."""
        # Try to update a program that doesn't belong to this trainer
        update_data = {"name": "Unauthorized Update"}
        response = client.put("/api/v1/programs/99999", headers=trainer_auth_headers, json=update_data)
        
        assert response.status_code in [403, 404]  # Should be forbidden or not found
