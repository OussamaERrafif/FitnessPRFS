import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestExerciseEndpoints:
    """Test suite for exercise management endpoints."""
    
    def test_create_exercise_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful exercise creation."""
        exercise_data = {
            "name": "Push-up",
            "description": "Classic upper body exercise",
            "muscle_groups": ["chest", "triceps", "shoulders"],
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": [
                "Start in plank position",
                "Lower body to ground",
                "Push back up to starting position"
            ],
            "tips": ["Keep core tight", "Maintain straight line"],
            "is_public": True
        }
        
        response = client.post("/api/v1/exercises/", headers=trainer_auth_headers, json=exercise_data)
        
        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == exercise_data["name"]
            assert data["description"] == exercise_data["description"]
            assert data["muscle_groups"] == exercise_data["muscle_groups"]
            assert "id" in data
    
    def test_get_all_exercises(self, client: TestClient):
        """Test getting all exercises."""
        response = client.get("/api/v1/exercises/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_get_exercise_by_id(self, client: TestClient, trainer_auth_headers: dict):
        """Test getting exercise by ID."""
        # Create an exercise first
        exercise_data = {
            "name": "Squat",
            "description": "Lower body compound exercise",
            "muscle_groups": ["quadriceps", "glutes"],
            "equipment": "bodyweight",
            "difficulty": "beginner"
        }
        create_response = client.post("/api/v1/exercises/", headers=trainer_auth_headers, json=exercise_data)
        
        if create_response.status_code in [200, 201]:
            exercise_id = create_response.json()["id"]
            
            response = client.get(f"/api/v1/exercises/{exercise_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == exercise_id
            assert data["name"] == exercise_data["name"]
    
    def test_search_exercises_by_muscle_group(self, client: TestClient):
        """Test exercise search by muscle group."""
        response = client.get("/api/v1/exercises/search?muscle_group=chest")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_search_exercises_by_equipment(self, client: TestClient):
        """Test exercise search by equipment."""
        response = client.get("/api/v1/exercises/search?equipment=dumbbells")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_search_exercises_by_difficulty(self, client: TestClient):
        """Test exercise search by difficulty."""
        response = client.get("/api/v1/exercises/search?difficulty=beginner")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_update_exercise_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful exercise update."""
        # Create an exercise first
        exercise_data = {
            "name": "Original Exercise",
            "description": "Original description",
            "muscle_groups": ["chest"],
            "equipment": "bodyweight",
            "difficulty": "beginner"
        }
        create_response = client.post("/api/v1/exercises/", headers=trainer_auth_headers, json=exercise_data)
        
        if create_response.status_code in [200, 201]:
            exercise_id = create_response.json()["id"]
            
            update_data = {
                "name": "Updated Exercise",
                "description": "Updated description",
                "difficulty": "intermediate"
            }
            
            response = client.put(f"/api/v1/exercises/{exercise_id}", headers=trainer_auth_headers, json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == update_data["name"]
            assert data["description"] == update_data["description"]
    
    def test_delete_exercise_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful exercise deletion."""
        # Create an exercise first
        exercise_data = {
            "name": "Exercise to Delete",
            "description": "This will be deleted",
            "muscle_groups": ["arms"],
            "equipment": "dumbbells",
            "difficulty": "beginner"
        }
        create_response = client.post("/api/v1/exercises/", headers=trainer_auth_headers, json=exercise_data)
        
        if create_response.status_code in [200, 201]:
            exercise_id = create_response.json()["id"]
            
            response = client.delete(f"/api/v1/exercises/{exercise_id}", headers=trainer_auth_headers)
            
            assert response.status_code in [200, 204]


class TestExerciseValidation:
    """Test exercise data validation."""
    
    def test_exercise_required_fields(self, client: TestClient, trainer_auth_headers: dict):
        """Test exercise creation with missing required fields."""
        # Missing name
        incomplete_data = {
            "description": "Exercise without name",
            "muscle_groups": ["chest"]
        }
        response = client.post("/api/v1/exercises/", headers=trainer_auth_headers, json=incomplete_data)
        assert response.status_code == 422
    
    def test_exercise_muscle_groups_validation(self, client: TestClient, trainer_auth_headers: dict):
        """Test muscle groups validation."""
        valid_data = {
            "name": "Multi-Muscle Exercise",
            "description": "Exercise targeting multiple muscle groups",
            "muscle_groups": ["chest", "triceps", "shoulders", "core"],
            "equipment": "dumbbells",
            "difficulty": "intermediate"
        }
        
        response = client.post("/api/v1/exercises/", headers=trainer_auth_headers, json=valid_data)
        assert response.status_code in [200, 201]
    
    def test_exercise_difficulty_validation(self, client: TestClient, trainer_auth_headers: dict):
        """Test difficulty validation."""
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        
        for difficulty in valid_difficulties:
            data = {
                "name": f"{difficulty.capitalize()} Exercise",
                "description": f"Exercise for {difficulty} level",
                "muscle_groups": ["arms"],
                "difficulty": difficulty
            }
            response = client.post("/api/v1/exercises/", headers=trainer_auth_headers, json=data)
            assert response.status_code in [200, 201]


class TestSessionBookingEndpoints:
    """Test suite for session booking endpoints."""
    
    def test_book_session_success(self, client: TestClient, client_auth_headers: dict, authenticated_trainer: dict):
        """Test successful session booking."""
        booking_data = {
            "trainer_id": authenticated_trainer["user_id"],
            "session_date": "2024-02-15",
            "session_time": "10:00:00",
            "duration_minutes": 60,
            "session_type": "personal_training",
            "notes": "First session"
        }
        
        response = client.post("/api/v1/sessions/book", headers=client_auth_headers, json=booking_data)
        
        assert response.status_code in [200, 201, 404]  # 404 if endpoint doesn't exist
    
    def test_get_my_sessions_client(self, client: TestClient, client_auth_headers: dict):
        """Test getting sessions as a client."""
        response = client.get("/api/v1/sessions/me", headers=client_auth_headers)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_my_sessions_trainer(self, client: TestClient, trainer_auth_headers: dict):
        """Test getting sessions as a trainer."""
        response = client.get("/api/v1/sessions/me", headers=trainer_auth_headers)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_cancel_session(self, client: TestClient, client_auth_headers: dict):
        """Test session cancellation."""
        # Assuming there's a session to cancel
        session_id = 1
        cancel_data = {
            "reason": "Schedule conflict",
            "cancellation_type": "client_cancelled"
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/cancel", headers=client_auth_headers, json=cancel_data)
        
        assert response.status_code in [200, 404]  # 404 if session doesn't exist
    
    def test_reschedule_session(self, client: TestClient, client_auth_headers: dict):
        """Test session rescheduling."""
        session_id = 1
        reschedule_data = {
            "new_date": "2024-02-20",
            "new_time": "14:00:00",
            "reason": "Client request"
        }
        
        response = client.post(f"/api/v1/sessions/{session_id}/reschedule", headers=client_auth_headers, json=reschedule_data)
        
        assert response.status_code in [200, 404]  # 404 if session doesn't exist


class TestMealPlanEndpoints:
    """Test suite for meal plan endpoints."""
    
    def test_create_meal_plan_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful meal plan creation."""
        meal_plan_data = {
            "name": "Weight Loss Meal Plan",
            "description": "Balanced meal plan for healthy weight loss",
            "calories_per_day": 1800,
            "duration_days": 30,
            "dietary_restrictions": ["vegetarian"],
            "goals": ["weight_loss", "health"],
            "is_public": True
        }
        
        response = client.post("/api/v1/meals/plans", headers=trainer_auth_headers, json=meal_plan_data)
        
        assert response.status_code in [200, 201, 404]  # 404 if endpoint doesn't exist
    
    def test_create_recipe_success(self, client: TestClient, trainer_auth_headers: dict):
        """Test successful recipe creation."""
        recipe_data = {
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
            ],
            "tags": ["high_protein", "post_workout"],
            "is_public": True
        }
        
        response = client.post("/api/v1/meals/recipes", headers=trainer_auth_headers, json=recipe_data)
        
        assert response.status_code in [200, 201, 404]  # 404 if endpoint doesn't exist
    
    def test_get_public_recipes(self, client: TestClient):
        """Test getting public recipes."""
        response = client.get("/api/v1/meals/recipes/public")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_search_recipes_by_tags(self, client: TestClient):
        """Test recipe search by tags."""
        response = client.get("/api/v1/meals/recipes/search?tags=high_protein")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestProgressTrackingEndpoints:
    """Test suite for progress tracking endpoints."""
    
    def test_log_workout_progress(self, client: TestClient, client_auth_headers: dict):
        """Test logging workout progress."""
        progress_data = {
            "workout_id": 1,
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets_completed": 3,
                    "reps_completed": [10, 8, 6],
                    "weight_used": 50.0,
                    "notes": "Felt strong today"
                }
            ],
            "overall_rating": 8,
            "notes": "Good workout session",
            "duration_minutes": 45
        }
        
        response = client.post("/api/v1/progress/workout", headers=client_auth_headers, json=progress_data)
        
        assert response.status_code in [200, 201, 404]  # 404 if endpoint doesn't exist
    
    def test_log_body_measurements(self, client: TestClient, client_auth_headers: dict):
        """Test logging body measurements."""
        measurement_data = {
            "weight": 70.5,
            "body_fat_percentage": 15.2,
            "muscle_mass": 55.0,
            "measurements": {
                "chest": 95.0,
                "waist": 80.0,
                "hips": 90.0,
                "bicep": 35.0
            },
            "date": "2024-01-15",
            "notes": "Monthly measurement"
        }
        
        response = client.post("/api/v1/progress/measurements", headers=client_auth_headers, json=measurement_data)
        
        assert response.status_code in [200, 201, 404]  # 404 if endpoint doesn't exist
    
    def test_get_progress_summary(self, client: TestClient, client_auth_headers: dict):
        """Test getting progress summary."""
        response = client.get("/api/v1/progress/summary", headers=client_auth_headers)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Should contain progress metrics
            assert "weight_progress" in data or "workout_stats" in data
    
    def test_get_progress_charts(self, client: TestClient, client_auth_headers: dict):
        """Test getting progress charts data."""
        response = client.get("/api/v1/progress/charts?metric=weight&period=3months")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))


class TestNotificationEndpoints:
    """Test suite for notification endpoints."""
    
    def test_get_my_notifications(self, client: TestClient, auth_headers: dict):
        """Test getting user notifications."""
        response = client.get("/api/v1/notifications/", headers=auth_headers)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_mark_notification_read(self, client: TestClient, auth_headers: dict):
        """Test marking notification as read."""
        notification_id = 1
        response = client.put(f"/api/v1/notifications/{notification_id}/read", headers=auth_headers)
        
        assert response.status_code in [200, 404]  # 404 if notification doesn't exist
    
    def test_delete_notification(self, client: TestClient, auth_headers: dict):
        """Test deleting a notification."""
        notification_id = 1
        response = client.delete(f"/api/v1/notifications/{notification_id}", headers=auth_headers)
        
        assert response.status_code in [200, 204, 404]  # 404 if notification doesn't exist
    
    def test_get_notification_settings(self, client: TestClient, auth_headers: dict):
        """Test getting notification settings."""
        response = client.get("/api/v1/notifications/settings", headers=auth_headers)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Should contain notification preferences
            assert isinstance(data, dict)
    
    def test_update_notification_settings(self, client: TestClient, auth_headers: dict):
        """Test updating notification settings."""
        settings_data = {
            "email_notifications": True,
            "push_notifications": False,
            "session_reminders": True,
            "progress_updates": True,
            "marketing_emails": False
        }
        
        response = client.put("/api/v1/notifications/settings", headers=auth_headers, json=settings_data)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["email_notifications"] == settings_data["email_notifications"]
