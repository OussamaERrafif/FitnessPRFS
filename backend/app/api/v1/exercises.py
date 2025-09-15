from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.exercise_service import exercise_service
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
    ExerciseFilter
)
from app.models.exercise import ExerciseCategory, MuscleGroup, ExerciseType
from app.models.user import User

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("/", response_model=List[ExerciseResponse])
async def get_exercises(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[ExerciseCategory] = Query(None),
    exercise_type: Optional[ExerciseType] = Query(None),
    primary_muscle_group: Optional[MuscleGroup] = Query(None),
    difficulty_level: Optional[int] = Query(None, ge=1, le=5),
    equipment_needed: Optional[str] = Query(None),
    max_duration_minutes: Optional[int] = Query(None, ge=1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get exercises with optional filtering."""
    filters = None
    if any([category, exercise_type, primary_muscle_group, difficulty_level, 
           equipment_needed, max_duration_minutes, search]):
        filters = ExerciseFilter(
            category=category,
            exercise_type=exercise_type,
            primary_muscle_group=primary_muscle_group,
            difficulty_level=difficulty_level,
            equipment_needed=equipment_needed,
            max_duration_minutes=max_duration_minutes,
            search=search
        )
    
    exercises = exercise_service.get_exercises(db, skip, limit, filters)
    return [ExerciseResponse.model_validate(exercise) for exercise in exercises]


@router.post("/", response_model=ExerciseResponse)
async def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new exercise (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can create exercises"
        )
    
    try:
        exercise = exercise_service.create_exercise(db, exercise_data, current_user.id)
        return ExerciseResponse.model_validate(exercise)
    except Exception as e:
        print(f"Exercise creation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create exercise: {str(e)}"
        )


@router.get("/seed", status_code=status.HTTP_201_CREATED)
async def seed_default_exercises(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Seed database with default exercises (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can seed exercises"
        )
    
    try:
        created_exercises = exercise_service.seed_default_exercises(db)
        return {
            "message": f"Seeded {len(created_exercises)} default exercises",
            "exercise_count": len(created_exercises)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to seed exercises"
        )


@router.get("/search", response_model=List[ExerciseResponse])
async def search_exercises(
    search_term: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search exercises by name or description."""
    exercises = exercise_service.search_exercises(db, search_term, limit)
    return [ExerciseResponse.model_validate(exercise) for exercise in exercises]


@router.get("/popular", response_model=List[ExerciseResponse])
async def get_popular_exercises(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get popular exercises."""
    exercises = exercise_service.get_popular_exercises(db, limit)
    return [ExerciseResponse.model_validate(exercise) for exercise in exercises]


@router.get("/categories")
async def get_exercise_categories():
    """Get all available exercise categories."""
    return {
        "categories": exercise_service.get_exercise_categories()
    }


@router.get("/muscle-groups")
async def get_muscle_groups():
    """Get all available muscle groups."""
    return {
        "muscle_groups": exercise_service.get_muscle_groups()
    }


@router.get("/types")
async def get_exercise_types():
    """Get all available exercise types."""
    return {
        "exercise_types": exercise_service.get_exercise_types()
    }


@router.get("/by-muscle/{muscle_group}", response_model=List[ExerciseResponse])
async def get_exercises_by_muscle_group(
    muscle_group: MuscleGroup,
    include_secondary: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get exercises targeting a specific muscle group."""
    exercises = exercise_service.get_exercises_by_muscle_group(
        db, muscle_group, include_secondary
    )
    return [ExerciseResponse.model_validate(exercise) for exercise in exercises]


@router.get("/by-equipment/{equipment}", response_model=List[ExerciseResponse])
async def get_exercises_by_equipment(
    equipment: str,
    db: Session = Depends(get_db)
):
    """Get exercises that require specific equipment."""
    exercises = exercise_service.get_exercises_by_equipment(db, equipment)
    return [ExerciseResponse.model_validate(exercise) for exercise in exercises]


@router.get("/bodyweight", response_model=List[ExerciseResponse])
async def get_bodyweight_exercises(
    db: Session = Depends(get_db)
):
    """Get all bodyweight exercises."""
    exercises = exercise_service.get_bodyweight_exercises(db)
    return [ExerciseResponse.model_validate(exercise) for exercise in exercises]


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    """Get exercise by ID."""
    exercise = exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    return ExerciseResponse.model_validate(exercise)


@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an exercise (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can update exercises"
        )
    
    updated_exercise = exercise_service.update_exercise(db, exercise_id, exercise_data)
    if not updated_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    return ExerciseResponse.model_validate(updated_exercise)


@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an exercise (soft delete - trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can delete exercises"
        )
    
    success = exercise_service.delete_exercise(db, exercise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    return {"message": "Exercise deleted successfully"}
