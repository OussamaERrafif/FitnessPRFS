from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from app.models.exercise import Exercise, ExerciseCategory, MuscleGroup, ExerciseType, DifficultyLevel
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
    ExerciseFilter
)


class ExerciseService:
    """Service for exercise-related operations."""
    
    # Default exercises data for seeding
    DEFAULT_EXERCISES = [
        {
            "name": "Push-ups",
            "description": "Classic bodyweight chest exercise",
            "category": ExerciseCategory.STRENGTH.value,
            "muscle_groups": ["chest", "triceps"],
            "equipment_needed": [],
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "default_sets": 3,
            "default_reps": "10-15",
            "is_public": True
        },
        {
            "name": "Squats",
            "description": "Fundamental lower body exercise",
            "category": ExerciseCategory.STRENGTH.value,
            "muscle_groups": ["quads", "glutes"],
            "equipment_needed": [],
            "difficulty_level": DifficultyLevel.BEGINNER.value,
            "default_sets": 3,
            "default_reps": "12-15",
            "is_public": True
        },
        {
            "name": "Running",
            "description": "Cardiovascular endurance exercise",
            "category": ExerciseCategory.CARDIO.value,
            "muscle_groups": ["full_body"],
            "equipment_needed": [],
            "difficulty_level": DifficultyLevel.BEGINNER.value,
            "default_duration": 1800,  # 30 minutes in seconds
            "is_public": True
        }
    ]
    
    @staticmethod
    def get_exercise_by_id(db: Session, exercise_id: int) -> Optional[Exercise]:
        """Get exercise by ID."""
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        return exercise
    
    @staticmethod
    def get_exercises(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[ExerciseFilter] = None
    ) -> List[Exercise]:
        """Get exercises with optional filtering."""
        query = db.query(Exercise).filter(Exercise.is_active == True)
        
        if filters:
            if filters.category:
                query = query.filter(Exercise.category == filters.category)
            
            if filters.exercise_type:
                query = query.filter(Exercise.exercise_type == filters.exercise_type)
            
            if filters.primary_muscle_group:
                query = query.filter(Exercise.primary_muscle_group == filters.primary_muscle_group)
            
            if filters.difficulty_level:
                query = query.filter(Exercise.difficulty_level == filters.difficulty_level)
            
            if filters.equipment_needed:
                query = query.filter(Exercise.equipment_needed.contains(filters.equipment_needed))
            
            if filters.max_duration_minutes:
                query = query.filter(Exercise.estimated_duration_minutes <= filters.max_duration_minutes)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Exercise.name.ilike(search_term),
                        Exercise.description.ilike(search_term)
                    )
                )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_exercise(db: Session, exercise_id: int, exercise_data: ExerciseUpdate, trainer_id: Optional[int] = None) -> Optional[Exercise]:
        """Update an exercise."""
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        
        # Authorization check - only creator or admin can update
        if trainer_id and exercise.created_by_trainer_id and exercise.created_by_trainer_id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this exercise"
            )
        
        update_dict = exercise_data.model_dump(exclude_unset=True)
        
        # Convert lists to JSON strings
        if 'secondary_muscle_groups' in update_dict and update_dict['secondary_muscle_groups']:
            update_dict['secondary_muscle_groups'] = str(update_dict['secondary_muscle_groups'])
        if 'equipment_needed' in update_dict and update_dict['equipment_needed']:
            update_dict['equipment_needed'] = str(update_dict['equipment_needed'])
        if 'instructions' in update_dict and update_dict['instructions']:
            update_dict['instructions'] = str(update_dict['instructions'])
        
        for field, value in update_dict.items():
            setattr(exercise, field, value)
        
        exercise.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(exercise)
        return exercise
    
    @staticmethod
    def delete_exercise(db: Session, exercise_id: int, trainer_id: Optional[int] = None) -> bool:
        """Soft delete an exercise."""
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        
        # Authorization check - only creator or admin can delete
        if trainer_id and exercise.created_by_trainer_id and exercise.created_by_trainer_id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this exercise"
            )
        
        exercise.is_active = False
        exercise.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def get_exercises_by_muscle_group(
        db: Session,
        muscle_group: str,
        include_secondary: bool = True
    ) -> List[Exercise]:
        """Get exercises targeting a specific muscle group."""
        # Since muscle_groups is stored as text/JSON, we need to search within it
        return db.query(Exercise).filter(
            Exercise.is_active == True,
            Exercise.muscle_groups.like(f'%{muscle_group}%')
        ).all()
    
    @staticmethod
    def search_exercises_by_name(db: Session, search_term: str) -> List[Exercise]:
        """Search exercises by name."""
        return db.query(Exercise).filter(
            Exercise.is_active == True,
            Exercise.name.ilike(f'%{search_term}%')
        ).all()
    
    @staticmethod
    def get_exercises_by_category(db: Session, category: ExerciseCategory) -> List[Exercise]:
        """Get exercises by category."""
        return db.query(Exercise).filter(
            Exercise.is_active == True,
            Exercise.category == category.value
        ).all()
    
    @staticmethod
    def get_exercises_by_equipment(db: Session, equipment: str) -> List[Exercise]:
        """Get exercises that require specific equipment."""
        return db.query(Exercise).filter(
            Exercise.is_active == True,
            Exercise.equipment_needed.contains(equipment)
        ).all()
    
    @staticmethod
    def get_bodyweight_exercises(db: Session) -> List[Exercise]:
        """Get all bodyweight exercises."""
        return db.query(Exercise).filter(
            Exercise.is_active == True,
            Exercise.exercise_type == ExerciseType.BODYWEIGHT
        ).all()
    
    @staticmethod
    def search_exercises(db: Session, search_term: str, limit: int = 20) -> List[Exercise]:
        """Search exercises by name or description."""
        search_pattern = f"%{search_term}%"
        return db.query(Exercise).filter(
            Exercise.is_active == True,
            or_(
                Exercise.name.ilike(search_pattern),
                Exercise.description.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_popular_exercises(db: Session, limit: int = 10) -> List[Exercise]:
        """Get popular exercises (mock implementation)."""
        # In a real implementation, you'd track usage statistics
        return db.query(Exercise).filter(
            Exercise.is_active == True
        ).order_by(Exercise.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def seed_default_exercises(db: Session) -> List[Exercise]:
        """Seed database with default exercises."""
        created_exercises = []
        
        for exercise_data in ExerciseService.DEFAULT_EXERCISES:
            # Check if exercise already exists
            existing = db.query(Exercise).filter(Exercise.name == exercise_data["name"]).first()
            if existing:
                continue
            
            # Convert lists to strings for database storage
            exercise_dict = exercise_data.copy()
            if exercise_dict.get('secondary_muscle_groups'):
                exercise_dict['secondary_muscle_groups'] = str(exercise_dict['secondary_muscle_groups'])
            if exercise_dict.get('equipment_needed'):
                exercise_dict['equipment_needed'] = str(exercise_dict['equipment_needed'])
            if exercise_dict.get('instructions'):
                exercise_dict['instructions'] = str(exercise_dict['instructions'])
            
            exercise = Exercise(**exercise_dict)
            db.add(exercise)
            created_exercises.append(exercise)
        
        if created_exercises:
            db.commit()
            for ex in created_exercises:
                db.refresh(ex)
        
        return created_exercises
    
    @staticmethod
    def create_exercise(db: Session, exercise_data: ExerciseCreate, trainer_id: Optional[int] = None) -> Exercise:
        """Create a new exercise."""
        import json
        
        # Convert list fields to JSON strings for database storage
        exercise_dict = exercise_data.model_dump()
        
        # Convert lists to JSON strings
        if exercise_dict.get('instructions') and isinstance(exercise_dict['instructions'], list):
            exercise_dict['instructions'] = json.dumps(exercise_dict['instructions'])
        
        if exercise_dict.get('muscle_groups') and isinstance(exercise_dict['muscle_groups'], list):
            exercise_dict['muscle_groups'] = json.dumps(exercise_dict['muscle_groups'])
            
        if exercise_dict.get('tips') and isinstance(exercise_dict['tips'], list):
            exercise_dict['tips'] = json.dumps(exercise_dict['tips'])
            
        if exercise_dict.get('alternatives') and isinstance(exercise_dict['alternatives'], list):
            exercise_dict['alternatives'] = json.dumps(exercise_dict['alternatives'])
        
        # Map schema fields to database fields
        if 'equipment' in exercise_dict:
            exercise_dict['equipment_needed'] = exercise_dict.pop('equipment')
        if 'difficulty' in exercise_dict:
            exercise_dict['difficulty_level'] = exercise_dict.pop('difficulty')
        if 'tips' in exercise_dict:
            # Store tips as safety_tips in the database
            exercise_dict['safety_tips'] = exercise_dict.pop('tips')
            if isinstance(exercise_dict['safety_tips'], list):
                exercise_dict['safety_tips'] = json.dumps(exercise_dict['safety_tips'])
        
        # Set trainer ID if provided
        if trainer_id:
            exercise_dict['created_by_trainer_id'] = trainer_id
        
        # Set default values
        exercise_dict.setdefault('is_active', True)
        exercise_dict.setdefault('is_public', True)
        
        # Ensure category is not None
        if not exercise_dict.get('category'):
            exercise_dict['category'] = 'strength'  # Default category
        
        # Create exercise
        exercise = Exercise(**exercise_dict)
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        
        return exercise
    
    @staticmethod
    def get_exercise_categories() -> List[str]:
        """Get all available exercise categories."""
        return [category.value for category in ExerciseCategory]
    
    @staticmethod
    def get_muscle_groups() -> List[str]:
        """Get all available muscle groups."""
        return [muscle.value for muscle in MuscleGroup]
    
    @staticmethod
    def get_exercise_types() -> List[str]:
        """Get all available exercise types."""
        return [ex_type.value for ex_type in ExerciseType]


# Global exercise service instance
exercise_service = ExerciseService()
