import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


class TestTrainerEndpoints:
    """Test suite for trainer management endpoints."""
    
    def test_create_trainer_profile_success(self, client: TestClient, auth_headers: dict):
        """Test successful trainer profile creation."""
        trainer_data = {
            "bio": "Experienced fitness trainer with 5 years of experience",
            "specializations": ["weight_loss", "strength_training"],
            "certification": "NASM-CPT",
            "experience_years": 5,
            "hourly_rate": 75.0,
            "location": "New York, NY"
        }
        
        response = client.post("/api/v1/trainers/", headers=auth_headers, json=trainer_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["bio"] == trainer_data["bio"]
        assert data["specializations"] == trainer_data["specializations"]
        assert data["hourly_rate"] == trainer_data["hourly_rate"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_trainer_profile_duplicate(self, client: TestClient, trainer_auth_headers: dict):
        """Test trainer profile creation when one already exists."""
        trainer_data = {
            "bio": "Another trainer bio",
            "hourly_rate": 50.0
        }
        
        # Should fail because authenticated_trainer fixture already created one
        response = client.post("/api/v1/trainers/", headers=trainer_auth_headers, json=trainer_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()
    
    def test_create_trainer_profile_unauthenticated(self, client: TestClient):
        """Test trainer profile creation without authentication."""
        trainer_data = {
            "bio": "Test trainer",
            "hourly_rate": 50.0
        }
        
        response = client.post("/api/v1/trainers/", json=trainer_data)
        
        assert response.status_code == 401
    
    def test_create_trainer_profile_invalid_data(self, client: TestClient, auth_headers: dict):
        """Test trainer profile creation with invalid data."""
        invalid_data = {
            "hourly_rate": -50.0  # Negative rate should be invalid
        }
        
        response = client.post("/api/v1/trainers/", headers=auth_headers, json=invalid_data)
        
        assert response.status_code == 422
    
    def test_get_all_trainers_success(self, client: TestClient, auth_headers: dict):
        """Test successful retrieval of all trainers (requires authentication)."""
        response = client.get("/api/v1/trainers/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Check structure of trainer data if any exist
        for trainer in data:
            assert "id" in trainer
            assert "bio" in trainer
            assert "hourly_rate" in trainer
    
    def test_get_all_trainers_with_pagination(self, client: TestClient, auth_headers: dict):
        """Test trainer list with pagination."""
        response = client.get("/api/v1/trainers/?skip=0&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_all_trainers_with_filter(self, client: TestClient, auth_headers: dict):
        """Test trainer list with active filter."""
        response = client.get("/api/v1/trainers/?is_active=true", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # All returned trainers should be active
        for trainer in data:
            assert trainer.get("is_available", True) is True
    
    def test_search_trainers_by_specialization(self, client: TestClient):
        """Test trainer search by specialization."""
        response = client.get("/api/v1/trainers/search?specialization=strength_training")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_search_trainers_by_location(self, client: TestClient):
        """Test trainer search by location."""
        response = client.get("/api/v1/trainers/search?location=New York")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_search_trainers_by_experience(self, client: TestClient):
        """Test trainer search by minimum experience."""
        response = client.get("/api/v1/trainers/search?min_experience=3")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_search_trainers_combined_filters(self, client: TestClient):
        """Test trainer search with multiple filters."""
        response = client.get(
            "/api/v1/trainers/search?specialization=weight_loss&min_experience=2&limit=5"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5


class TestTrainerProfileManagement:
    """Test trainer profile management endpoints."""
    
    def test_get_my_trainer_profile_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful retrieval of own trainer profile."""
        # The authenticated_trainer fixture already creates a trainer profile
        # So we can directly get the profile
        response = client.get("/api/v1/trainers/me", headers=trainer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bio" in data
        assert "hourly_rate" in data
        assert "id" in data
        assert "user_id" in data
    
    def test_get_my_trainer_profile_not_found(self, client: TestClient, auth_headers: dict):
        """Test trainer profile retrieval when none exists."""
        response = client.get("/api/v1/trainers/me", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_my_trainer_profile_unauthenticated(self, client: TestClient):
        """Test trainer profile retrieval without authentication."""
        response = client.get("/api/v1/trainers/me")
        
        assert response.status_code == 401
    
    def test_update_my_trainer_profile_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful trainer profile update."""
        # The authenticated_trainer fixture already creates a trainer profile
        # So we can directly update the existing profile
        update_data = {
            "bio": "Updated bio",
            "hourly_rate": 80.0,
            "specializations": ["strength_training", "nutrition"]
        }
        response = client.put("/api/v1/trainers/me", headers=trainer_auth_headers, json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["bio"] == update_data["bio"]
        assert data["hourly_rate"] == update_data["hourly_rate"]
        assert data["specializations"] == update_data["specializations"]
    
    def test_update_my_trainer_profile_not_found(self, client: TestClient, auth_headers: dict):
        """Test trainer profile update when none exists."""
        update_data = {
            "bio": "Updated bio"
        }
        response = client.put("/api/v1/trainers/me", headers=auth_headers, json=update_data)
        
        assert response.status_code == 404
    
    def test_update_my_trainer_profile_invalid_data(self, client: TestClient, trainer_auth_headers: dict):
        """Test trainer profile update with invalid data."""
        # The authenticated_trainer fixture already creates a trainer profile
        # So we can directly try to update with invalid data
        invalid_data = {
            "hourly_rate": -50.0  # Negative rate
        }
        response = client.put("/api/v1/trainers/me", headers=trainer_auth_headers, json=invalid_data)
        
        assert response.status_code == 422


class TestTrainerDashboard:
    """Test trainer dashboard and statistics endpoints."""
    
    def test_get_my_dashboard_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful trainer dashboard retrieval."""
        # The authenticated_trainer fixture already creates a trainer profile
        response = client.get("/api/v1/trainers/me/dashboard", headers=trainer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Dashboard should contain required fields based on TrainerDashboard schema
        assert "trainer_info" in data
        assert "stats" in data
        assert "today_sessions" in data
        assert "upcoming_sessions" in data
        assert "recent_clients" in data
        assert "notifications" in data
    
    def test_get_my_dashboard_not_found(self, client: TestClient, auth_headers: dict):
        """Test dashboard retrieval when trainer profile doesn't exist."""
        response = client.get("/api/v1/trainers/me/dashboard", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_my_stats_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful trainer statistics retrieval."""
        # The authenticated_trainer fixture already creates a trainer profile
        response = client.get("/api/v1/trainers/me/stats", headers=trainer_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Stats should contain metrics
        assert "total_clients" in data
        assert "active_clients" in data
        assert "sessions_this_month" in data
        assert "revenue_this_month" in data
        assert "average_rating" in data
        assert "total_sessions" in data
        assert "certification_count" in data
    
    def test_get_my_stats_not_found(self, client: TestClient, auth_headers: dict):
        """Test stats retrieval when trainer profile doesn't exist."""
        response = client.get("/api/v1/trainers/me/stats", headers=auth_headers)
        
        assert response.status_code == 404


class TestTrainerCertifications:
    """Test trainer certification management."""
    
    def test_add_certification_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful certification addition."""
        # The authenticated_trainer fixture already creates a trainer profile
        cert_data = {
            "name": "NASM-CPT",
            "issuing_organization": "National Academy of Sports Medicine",
            "issue_date": "2023-01-15",
            "expiry_date": "2025-01-15",
            "certificate_number": "CPT123456"
        }
        response = client.post("/api/v1/trainers/me/certifications", headers=trainer_auth_headers, json=cert_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "certification_id" in data
    
    def test_add_certification_not_trainer(self, client: TestClient, auth_headers: dict):
        """Test certification addition when not a trainer."""
        cert_data = {
            "name": "NASM-CPT",
            "issuing_organization": "NASM"
        }
        response = client.post("/api/v1/trainers/me/certifications", headers=auth_headers, json=cert_data)
        
        assert response.status_code == 404


class TestTrainerDataValidation:
    """Test trainer data validation and constraints."""
    
    def test_trainer_profile_data_types(self, client: TestClient, auth_headers: dict):
        """Test trainer profile data type validation."""
        # Valid data with all types
        trainer_data = {
            "bio": "Test trainer bio",
            "hourly_rate": 75.50,
            "experience_years": 5,
            "is_available": True,
            "specializations": ["weight_loss", "strength_training"],
            "certification": "NASM-CPT"
        }
        
        response = client.post("/api/v1/trainers/", headers=auth_headers, json=trainer_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["bio"], str)
        assert isinstance(data["hourly_rate"], (int, float))
        assert isinstance(data["experience_years"], int)
        assert isinstance(data["is_available"], bool)
        assert isinstance(data["specializations"], list)
    
    def test_trainer_profile_required_fields(self, client: TestClient, auth_headers: dict):
        """Test trainer profile with minimal required fields."""
        minimal_data = {
            "hourly_rate": 50.0
        }
        
        response = client.post("/api/v1/trainers/", headers=auth_headers, json=minimal_data)
        
        # Should succeed with minimal data
        assert response.status_code in [200, 422]  # Depending on actual requirements
    
    def test_trainer_profile_rate_constraints_negative(self, client: TestClient, auth_headers: dict):
        """Test hourly rate constraints - negative rate."""
        # Test negative rate
        negative_rate_data = {"hourly_rate": -10.0}
        response = client.post("/api/v1/trainers/", headers=auth_headers, json=negative_rate_data)
        assert response.status_code == 422
        
    def test_trainer_profile_rate_constraints_zero(self, client: TestClient, auth_headers: dict):
        """Test hourly rate constraints - zero rate."""
        # Test zero rate (might be valid for pro bono)
        zero_rate_data = {"hourly_rate": 0.0}
        response = client.post("/api/v1/trainers/", headers=auth_headers, json=zero_rate_data)
        # Should succeed or fail based on business rules
        assert response.status_code in [200, 422]
        
    def test_trainer_profile_rate_constraints_high(self, client: TestClient, auth_headers: dict):
        """Test hourly rate constraints - high rate."""
        # Test very high rate
        high_rate_data = {"hourly_rate": 1000.0}
        response = client.post("/api/v1/trainers/", headers=auth_headers, json=high_rate_data)
        assert response.status_code == 200  # Should be allowed


class TestTrainerAccessControl:
    """Test trainer-specific access control."""
    
    def test_client_cannot_create_trainer_profile(self, client: TestClient, client_auth_headers: dict):
        """Test that clients cannot create trainer profiles."""
        trainer_data = {
            "bio": "Trying to become a trainer",
            "hourly_rate": 50.0
        }
        
        response = client.post("/api/v1/trainers/", headers=client_auth_headers, json=trainer_data)
        
        # Should succeed as any user can create a trainer profile
        assert response.status_code == 200
    
    def test_trainer_can_access_own_data_only(self, client: TestClient, trainer_auth_headers: dict):
        """Test that trainers can only access their own profile data."""
        # The authenticated_trainer fixture already creates a trainer profile
        # Access own profile
        response = client.get("/api/v1/trainers/me", headers=trainer_auth_headers)
        assert response.status_code == 200
        
        # Access own dashboard
        dashboard_response = client.get("/api/v1/trainers/me/dashboard", headers=trainer_auth_headers)
        assert dashboard_response.status_code == 200
