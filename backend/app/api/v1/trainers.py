from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.trainer_service import trainer_service
from app.schemas.trainer import (
    TrainerCreate,
    TrainerUpdate,
    TrainerResponse,
    TrainerCertificationCreate,
    TrainerCertificationUpdate,
    TrainerAvailabilityCreate,
    TrainerAvailabilityUpdate,
    TrainerStats,
    TrainerDashboard
)
from app.models.user import User

router = APIRouter(prefix="/trainers", tags=["Trainers"])


@router.post("/", response_model=TrainerResponse)
async def create_trainer_profile(
    trainer_data: TrainerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a trainer profile for a user."""
    try:
        # Set the user_id from the authenticated user
        trainer_data.user_id = current_user.id
        trainer = trainer_service.create_trainer(db, trainer_data)
        return TrainerResponse.model_validate(trainer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trainer profile"
        )


@router.get("/", response_model=List[TrainerResponse])
async def get_all_trainers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all trainers (auth required for tests)."""
    trainers = trainer_service.get_all_trainers(db, skip, limit, is_active)
    return [TrainerResponse.model_validate(trainer) for trainer in trainers]


@router.get("/search", response_model=List[TrainerResponse])
async def search_trainers(
    specialization: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    min_experience: Optional[int] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search trainers by criteria."""
    trainers = trainer_service.search_trainers(
        db, specialization, location, min_experience, skip, limit
    )
    return [TrainerResponse.model_validate(trainer) for trainer in trainers]


@router.get("/me", response_model=TrainerResponse)
async def get_my_trainer_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's trainer profile."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    return TrainerResponse.model_validate(trainer)


@router.put("/me", response_model=TrainerResponse)
async def update_my_trainer_profile(
    trainer_data: TrainerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's trainer profile."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    updated_trainer = trainer_service.update_trainer(db, trainer.id, trainer_data)
    if not updated_trainer:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update trainer profile"
        )
    
    return TrainerResponse.model_validate(updated_trainer)


@router.get("/me/dashboard", response_model=TrainerDashboard)
async def get_my_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trainer dashboard data."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    dashboard = trainer_service.get_trainer_dashboard(db, trainer.id)
    return dashboard


@router.get("/me/stats", response_model=TrainerStats)
async def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trainer statistics."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    stats = trainer_service.get_trainer_stats(db, trainer.id)
    return stats


@router.post("/me/certifications")
async def add_certification(
    cert_data: TrainerCertificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a certification to current trainer."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    certification = trainer_service.add_certification(db, trainer.id, cert_data)
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add certification"
        )
    
    return {"message": "Certification added successfully", "certification_id": certification.id}


@router.put("/certifications/{certification_id}")
async def update_certification(
    certification_id: int,
    cert_data: TrainerCertificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a certification."""
    # Verify ownership of certification
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    certification = trainer_service.update_certification(db, certification_id, cert_data)
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found"
        )
    
    return {"message": "Certification updated successfully"}


@router.get("/me/certifications")
async def get_my_certifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current trainer's certifications."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    certifications = trainer_service.get_trainer_certifications(db, trainer.id)
    return certifications


@router.post("/me/availability")
async def set_availability(
    availability_data: TrainerAvailabilityCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set trainer availability for a day."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    availability = trainer_service.set_availability(db, trainer.id, availability_data)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set availability"
        )
    
    return {"message": "Availability updated successfully", "availability_id": availability.id}


@router.get("/me/availability")
async def get_my_availability(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current trainer's availability schedule."""
    trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer profile not found"
        )
    
    availability = trainer_service.get_trainer_availability(db, trainer.id)
    return availability


@router.get("/{trainer_id}", response_model=TrainerResponse)
async def get_trainer_profile(
    trainer_id: int,
    db: Session = Depends(get_db)
):
    """Get trainer profile by ID (public endpoint)."""
    trainer = trainer_service.get_trainer_by_id(db, trainer_id)
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    
    return TrainerResponse.model_validate(trainer)


@router.put("/{trainer_id}", response_model=TrainerResponse)
async def update_trainer_profile(
    trainer_id: int,
    trainer_data: TrainerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update trainer profile by ID (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update other trainer profiles"
        )
    
    updated_trainer = trainer_service.update_trainer(db, trainer_id, trainer_data)
    if not updated_trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    
    return TrainerResponse.model_validate(updated_trainer)


@router.get("/{trainer_id}/clients")
async def get_trainer_clients_by_id(
    trainer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trainer's clients by trainer ID."""
    # Check if user is the trainer or an admin
    if current_user.role.value == "trainer":
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or trainer.id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other trainer's clients"
            )
    elif current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can view client lists"
        )
    
    clients = trainer_service.get_trainer_clients(db, trainer_id, skip, limit)
    return clients


@router.get("/{trainer_id}/sessions")
async def get_trainer_sessions(
    trainer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trainer's sessions."""
    # Check if user is the trainer or an admin
    if current_user.role.value == "trainer":
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or trainer.id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other trainer's sessions"
            )
    elif current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can view session lists"
        )
    
    sessions = trainer_service.get_trainer_sessions(db, trainer_id)
    return sessions


@router.get("/{trainer_id}/stats", response_model=TrainerStats)
async def get_trainer_stats_by_id(
    trainer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trainer statistics by ID (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view other trainer statistics"
        )
    
    stats = trainer_service.get_trainer_stats(db, trainer_id)
    return stats
