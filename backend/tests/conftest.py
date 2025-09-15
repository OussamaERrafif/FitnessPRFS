import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.session import get_db, Base
from app.models.user import User
from app.models.trainer import Trainer
from app.models.client import Client
from app.services.auth_service import auth_service
from app.schemas.auth import RegisterRequest


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db_session = TestingSessionLocal()
    
    try:
        yield db_session
    finally:
        db_session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with dependency overrides."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "role": "trainer"
    }


@pytest.fixture
def test_trainer_data():
    """Sample trainer data for testing."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"trainer_{unique_id}@example.com",
        "username": f"testtrainer_{unique_id}",
        "password": "TrainerPassword123!",
        "full_name": "Test Trainer",
        "role": "trainer",
        "bio": "Experienced fitness trainer",
        "hourly_rate": 50.0,
        "certifications": ["NASM-CPT", "ACSM-EP"]
    }


@pytest.fixture
def test_client_data():
    """Sample client data for testing."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"client_{unique_id}@example.com",
        "username": f"testclient_{unique_id}",
        "password": "ClientPassword123!",
        "full_name": "Test Client",
        "role": "client",
        "age": 25,
        "height": 175.0,
        "weight": 70.0,
        "fitness_level": "intermediate"
    }


@pytest.fixture
def authenticated_user(client: TestClient, test_user_data: dict) -> dict:
    """Create and authenticate a test user, return user data with tokens."""
    # Register user
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Login to get tokens
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    auth_data = login_response.json()
    return {
        **test_user_data,
        "access_token": auth_data["access_token"],
        "refresh_token": auth_data["refresh_token"],
        "user_id": auth_data["user_id"]
    }


@pytest.fixture
def authenticated_trainer(client: TestClient, test_trainer_data: dict, db: Session) -> dict:
    """Create and authenticate a test trainer, return trainer data with tokens."""
    # Register trainer
    response = client.post("/api/v1/auth/register", json=test_trainer_data)
    assert response.status_code == 201
    user_id = response.json()["user_id"]
    
    # Create the associated Trainer record manually in the database
    from app.models.trainer import Trainer
    from app.models.user import User
    
    trainer_record = Trainer(
        user_id=user_id,
        bio=test_trainer_data.get("bio", "Experienced fitness trainer"),
        certification=test_trainer_data.get("certification", "NASM-CPT"),
        hourly_rate=test_trainer_data.get("hourly_rate", 50.0),
        years_of_experience=3,
        specializations='["strength_training", "weight_loss"]'  # JSON string
    )
    db.add(trainer_record)
    db.commit()
    db.refresh(trainer_record)
    
    # Login to get tokens
    login_data = {
        "email": test_trainer_data["email"],
        "password": test_trainer_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    auth_data = login_response.json()
    return {
        **test_trainer_data,
        "access_token": auth_data["access_token"],
        "refresh_token": auth_data["refresh_token"],
        "user_id": auth_data["user_id"],
        "trainer_id": trainer_record.id
    }


@pytest.fixture
def authenticated_client_user(client: TestClient, test_client_data: dict, db: Session) -> dict:
    """Create and authenticate a test client, return client data with tokens."""
    # Register client
    response = client.post("/api/v1/auth/register", json=test_client_data)
    assert response.status_code == 201
    user_id = response.json()["user_id"]
    
    # Create the associated Client record manually in the database
    from app.models.client import Client
    from app.models.user import User
    
    client_record = Client(
        user_id=user_id,
        age=test_client_data.get("age", 25),
        height=test_client_data.get("height", 175.0),
        current_weight=test_client_data.get("current_weight", 70.0),
        fitness_level=test_client_data.get("fitness_level", "intermediate"),
        fitness_goals=["general_fitness", "strength_gain"]  # Use proper field name
    )
    db.add(client_record)
    db.commit()
    db.refresh(client_record)
    
    print(f"DEBUG: Created Client with ID: {client_record.id}")
    
    # Login to get tokens
    login_data = {
        "email": test_client_data["email"],
        "password": test_client_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    auth_data = login_response.json()
    return {
        **test_client_data,
        "access_token": auth_data["access_token"],
        "refresh_token": auth_data["refresh_token"],
        "user_id": auth_data["user_id"],
        "client_id": client_record.id
    }


@pytest.fixture
def auth_headers(authenticated_user: dict) -> dict:
    """Return authentication headers for API requests."""
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def trainer_auth_headers(authenticated_trainer: dict) -> dict:
    """Return authentication headers for trainer API requests."""
    return {"Authorization": f"Bearer {authenticated_trainer['access_token']}"}


@pytest.fixture
def client_auth_headers(authenticated_client_user: dict) -> dict:
    """Return authentication headers for client API requests."""
    return {"Authorization": f"Bearer {authenticated_client_user['access_token']}"}


# Sample data fixtures for various entities
@pytest.fixture
def sample_exercise_data():
    """Sample exercise data for testing."""
    return {
        "name": "Push-ups",
        "description": "Upper body exercise targeting chest and arms",
        "muscle_groups": ["chest", "triceps", "shoulders"],
        "equipment": "bodyweight",
        "difficulty": "beginner",
        "instructions": ["Start in plank position", "Lower body to ground", "Push back up"]
    }


@pytest.fixture
def sample_program_data():
    """Sample training program data for testing."""
    return {
        "name": "Beginner Strength Program",
        "description": "6-week strength building program for beginners",
        "duration_weeks": 6,
        "sessions_per_week": 3,
        "difficulty": "beginner",
        "goals": ["strength", "muscle_building"]
    }


@pytest.fixture
def sample_meal_plan_data():
    """Sample meal plan data for testing."""
    return {
        "name": "Healthy Weight Loss Plan",
        "description": "Balanced meal plan for healthy weight loss",
        "calories_per_day": 1800,
        "duration_days": 30,
        "dietary_restrictions": ["vegetarian"]
    }


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing."""
    return {
        "name": "Protein Smoothie",
        "description": "High-protein post-workout smoothie",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 1,
        "calories_per_serving": 250,
        "protein_per_serving": 30,
        "ingredients": [
            {"name": "protein powder", "amount": 30, "unit": "g"},
            {"name": "banana", "amount": 1, "unit": "piece"},
            {"name": "almond milk", "amount": 250, "unit": "ml"}
        ],
        "instructions": [
            "Add all ingredients to blender",
            "Blend until smooth",
            "Serve immediately"
        ]
    }


@pytest.fixture
def test_client_for_program(authenticated_client_user: dict) -> int:
    """Return the client ID for program testing."""
    client_id = authenticated_client_user["client_id"]
    print(f"DEBUG: test_client_for_program returning ID: {client_id}")
    return client_id
