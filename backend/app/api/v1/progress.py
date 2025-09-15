from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.progress_log_service import progress_log_service
from app.schemas.progress_log import (
    ProgressLogCreate,
    ProgressLogUpdate,
    ProgressLogResponse,
    ProgressLogFilter,
    ProgressStats,
    WorkoutSummary
)
from app.models.progress_log import LogType
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post("/", response_model=ProgressLogResponse, status_code=status.HTTP_201_CREATED)
async def create_progress_log(
    log_data: ProgressLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new progress log entry."""
    try:
        progress_log = progress_log_service.create_progress_log(db, log_data)
        return ProgressLogResponse.model_validate(progress_log)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create progress log"
        )


@router.get("/client/{client_id}", response_model=List[ProgressLogResponse])
async def get_client_progress_logs(
    client_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    log_type: Optional[LogType] = Query(None),
    exercise_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress logs for a client."""
    # Check permissions
    if current_user.role.value not in ["trainer", "admin"]:
        # Check if user is the client
        from app.services.client_service import client_service
        client = client_service.get_client_by_id(db, client_id)
        if not client or client.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's progress"
            )
    
    filters = None
    if any([log_type, exercise_id, start_date, end_date]):
        filters = ProgressLogFilter(
            log_type=log_type,
            exercise_id=exercise_id,
            start_date=start_date,
            end_date=end_date
        )
    
    logs = progress_log_service.get_client_progress_logs(db, client_id, skip, limit, filters)
    return [ProgressLogResponse.model_validate(log) for log in logs]


@router.get("/client/{client_id}/stats", response_model=ProgressStats)
async def get_client_progress_stats(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress statistics for a client."""
    # Check permissions
    if current_user.role.value not in ["trainer", "admin"]:
        from app.services.client_service import client_service
        client = client_service.get_client_by_id(db, client_id)
        if not client or client.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's statistics"
            )
    
    stats = progress_log_service.get_progress_stats(db, client_id)
    return stats


@router.get("/{log_id}", response_model=ProgressLogResponse)
async def get_progress_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress log by ID."""
    progress_log = progress_log_service.get_progress_log_by_id(db, log_id)
    if not progress_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress log not found"
        )
    
    # Check permissions
    if current_user.role.value not in ["trainer", "admin"]:
        from app.services.client_service import client_service
        client = client_service.get_client_by_id(db, progress_log.client_id)
        if not client or client.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's progress"
            )
    
    return ProgressLogResponse.model_validate(progress_log)


@router.put("/{log_id}", response_model=ProgressLogResponse)
async def update_progress_log(
    log_id: int,
    log_data: ProgressLogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a progress log entry."""
    progress_log = progress_log_service.get_progress_log_by_id(db, log_id)
    if not progress_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress log not found"
        )
    
    # Check permissions
    if current_user.role.value not in ["trainer", "admin"]:
        from app.services.client_service import client_service
        client = client_service.get_client_by_id(db, progress_log.client_id)
        if not client or client.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update other client's progress"
            )
    
    updated_log = progress_log_service.update_progress_log(db, log_id, log_data)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update progress log"
        )
    
    return ProgressLogResponse.model_validate(updated_log)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_progress_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a progress log entry."""
    progress_log = progress_log_service.get_progress_log_by_id(db, log_id)
    if not progress_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress log not found"
        )
    
    # Check permissions
    if current_user.role.value not in ["trainer", "admin"]:
        from app.services.client_service import client_service
        client = client_service.get_client_by_id(db, progress_log.user_id)
        if not client or client.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete other client's progress"
            )
    
    success = progress_log_service.delete_progress_log(db, log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete progress log"
        )
    
    return None  # 204 No Content should return no body
