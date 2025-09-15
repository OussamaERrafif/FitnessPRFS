from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.program_service import program_service
from app.schemas.program import (
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
    ProgramExerciseCreate,
    ProgramExerciseUpdate,
    ProgramFilter,
    ProgramAssignment
)
from app.models.program import ProgramStatus
from app.models.exercise import DifficultyLevel
from app.models.user import User

router = APIRouter(prefix="/programs", tags=["Programs"])


@router.post("/", response_model=ProgramResponse)
async def create_program(
    program_data: ProgramCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new fitness program (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can create programs"
        )
    
    # Get trainer record for the current user
    from app.services.trainer_service import trainer_service
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    try:
        program = program_service.create_program(db, program_data, trainer.id)
        return ProgramResponse.model_validate(program)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create program: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create program"
        )


@router.get("/", response_model=List[ProgramResponse])
async def get_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[ProgramStatus] = Query(None),
    difficulty_level: Optional[DifficultyLevel] = Query(None),
    trainer_id: Optional[int] = Query(None),
    duration_weeks_min: Optional[int] = Query(None, ge=1),
    duration_weeks_max: Optional[int] = Query(None, ge=1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get programs with optional filtering."""
    filters = None
    if any([status, difficulty_level, trainer_id, duration_weeks_min, 
           duration_weeks_max, search]):
        filters = ProgramFilter(
            status=status,
            difficulty_level=difficulty_level,
            trainer_id=trainer_id,
            duration_weeks_min=duration_weeks_min,
            duration_weeks_max=duration_weeks_max,
            search=search
        )
    
    programs = program_service.get_programs(db, skip, limit, filters)
    return [ProgramResponse.model_validate(program) for program in programs]


@router.get("/popular", response_model=List[ProgramResponse])
async def get_popular_programs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get popular programs."""
    programs = program_service.get_popular_programs(db, limit)
    return [ProgramResponse.model_validate(program) for program in programs]


@router.get("/search", response_model=List[ProgramResponse])
async def search_programs(
    search_term: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search programs by name or description."""
    programs = program_service.search_programs(db, search_term, limit)
    return [ProgramResponse.model_validate(program) for program in programs]


@router.get("/trainer/{trainer_id}", response_model=List[ProgramResponse])
async def get_trainer_programs(
    trainer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get programs created by a trainer."""
    # Check permissions
    if current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or trainer.id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other trainer's programs"
            )
    elif current_user.role.value not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can view trainer programs"
        )
    
    programs = program_service.get_trainer_programs(db, trainer_id)
    return [ProgramResponse.model_validate(program) for program in programs]


@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(
    program_id: int,
    db: Session = Depends(get_db)
):
    """Get program by ID."""
    program = program_service.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    return ProgramResponse.model_validate(program)


@router.put("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a program."""
    # Check if user can update this program
    program = program_service.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    if current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or program.trainer_id != trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update other trainer's programs"
            )
    elif current_user.role.value not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can update programs"
        )
    
    updated_program = program_service.update_program(db, program_id, program_data)
    if not updated_program:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update program"
        )
    
    return ProgramResponse.model_validate(updated_program)


@router.delete("/{program_id}")
async def delete_program(
    program_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a program (soft delete)."""
    # Check if user can delete this program
    program = program_service.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    if current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or program.trainer_id != trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete other trainer's programs"
            )
    elif current_user.role.value not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can delete programs"
        )
    
    success = program_service.delete_program(db, program_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete program"
        )
    
    return {"message": "Program deleted successfully"}


@router.post("/{program_id}/exercises")
async def add_exercise_to_program(
    program_id: int,
    exercise_data: ProgramExerciseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add an exercise to a program."""
    # Check permissions (same as update program)
    program = program_service.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    if current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or program.trainer_id != trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify other trainer's programs"
            )
    elif current_user.role.value not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can modify programs"
        )
    
    program_exercise = program_service.add_exercise_to_program(db, program_id, exercise_data)
    if not program_exercise:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add exercise to program"
        )
    
    return {"message": "Exercise added to program successfully", "exercise_id": program_exercise.id}


@router.get("/{program_id}/exercises")
async def get_program_exercises(
    program_id: int,
    db: Session = Depends(get_db)
):
    """Get all exercises in a program."""
    program = program_service.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    exercises = program_service.get_program_exercises(db, program_id)
    return exercises
