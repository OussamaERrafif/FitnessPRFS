from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.session_booking_service import session_booking_service
from app.schemas.session_booking import (
    SessionBookingCreate,
    SessionBookingUpdate,
    SessionBookingResponse,
    SessionBookingFilter,
    TimeSlot,
    SessionSummary
)
from app.models.session_booking import SessionStatus
from app.models.user import User

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=SessionBookingResponse)
async def create_session_booking(
    booking_data: SessionBookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new session booking."""
    try:
        booking = session_booking_service.create_session_booking(db, booking_data)
        return SessionBookingResponse.model_validate(booking)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session booking"
        )


@router.get("/", response_model=List[SessionBookingResponse])
async def get_session_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    trainer_id: Optional[int] = Query(None),
    status: Optional[SessionStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    session_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get session bookings with optional filtering."""
    # Apply role-based filtering
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if client:
            client_id = client.id  # Only show client's own sessions
        else:
            return []  # No client profile found
    elif current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if trainer:
            trainer_id = trainer.id  # Only show trainer's own sessions
        else:
            return []  # No trainer profile found
    # Admins can see all sessions
    
    filters = None
    if any([client_id, trainer_id, status, start_date, end_date, session_type]):
        filters = SessionBookingFilter(
            client_id=client_id,
            trainer_id=trainer_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            session_type=session_type
        )
    
    bookings = session_booking_service.get_session_bookings(db, skip, limit, filters)
    return [SessionBookingResponse.model_validate(booking) for booking in bookings]


@router.get("/trainer/{trainer_id}/schedule")
async def get_trainer_schedule(
    trainer_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trainer's schedule for a date range."""
    # Check permissions
    if current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or trainer.id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other trainer's schedule"
            )
    elif current_user.role.value not in ["admin"]:
        # Clients can view trainer schedules for booking purposes
        pass
    
    schedule = session_booking_service.get_trainer_schedule(db, trainer_id, start_date, end_date)
    return schedule


@router.get("/trainer/{trainer_id}/availability/{date}")
async def get_available_time_slots(
    trainer_id: int,
    date: date,
    duration_minutes: int = Query(60, ge=15, le=240),
    db: Session = Depends(get_db)
):
    """Get available time slots for a trainer on a specific date."""
    try:
        slots = session_booking_service.get_available_time_slots(db, trainer_id, date, duration_minutes)
        return {"available_slots": slots}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available time slots"
        )


@router.get("/client/{client_id}/sessions", response_model=List[SessionBookingResponse])
async def get_client_sessions(
    client_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get client's session history."""
    # Check permissions
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or client.id != client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's sessions"
            )
    elif current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients, trainers, and admins can view session history"
        )
    
    sessions = session_booking_service.get_client_sessions(db, client_id, start_date, end_date)
    return [SessionBookingResponse.model_validate(session) for session in sessions]


@router.get("/{booking_id}", response_model=SessionBookingResponse)
async def get_session_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get session booking by ID."""
    booking = session_booking_service.get_session_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session booking not found"
        )
    
    # Check permissions
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or booking.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's bookings"
            )
    elif current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or booking.trainer_id != trainer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other trainer's bookings"
            )
    # Admins can view all bookings
    
    return SessionBookingResponse.model_validate(booking)


@router.put("/{booking_id}", response_model=SessionBookingResponse)
async def update_session_booking(
    booking_id: int,
    booking_data: SessionBookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a session booking."""
    booking = session_booking_service.get_session_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session booking not found"
        )
    
    # Check permissions (only involved parties can update)
    can_update = False
    if current_user.role.value == "admin":
        can_update = True
    elif current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if client and booking.client_id == client.id:
            can_update = True
    elif current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if trainer and booking.trainer_id == trainer.id:
            can_update = True
    
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update this booking"
        )
    
    try:
        updated_booking = session_booking_service.update_session_booking(db, booking_id, booking_data)
        if not updated_booking:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update booking"
            )
        
        return SessionBookingResponse.model_validate(updated_booking)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session booking"
        )


@router.post("/{booking_id}/cancel")
async def cancel_session_booking(
    booking_id: int,
    reason: str = Query("", max_length=500),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a session booking."""
    # Similar permission check as update
    booking = session_booking_service.get_session_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session booking not found"
        )
    
    # Check permissions
    can_cancel = False
    if current_user.role.value == "admin":
        can_cancel = True
    elif current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if client and booking.client_id == client.id:
            can_cancel = True
    elif current_user.role.value == "trainer":
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if trainer and booking.trainer_id == trainer.id:
            can_cancel = True
    
    if not can_cancel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot cancel this booking"
        )
    
    cancelled_booking = session_booking_service.cancel_session_booking(db, booking_id, reason)
    if not cancelled_booking:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        )
    
    return {"message": "Session cancelled successfully"}


@router.post("/{booking_id}/confirm")
async def confirm_session_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm a pending session booking (trainers only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can confirm sessions"
        )
    
    confirmed_booking = session_booking_service.confirm_session_booking(db, booking_id)
    if not confirmed_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session booking not found or cannot be confirmed"
        )
    
    return {"message": "Session confirmed successfully"}


@router.post("/{booking_id}/complete")
async def complete_session_booking(
    booking_id: int,
    session_notes: Optional[str] = Query(None, max_length=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a session as completed (trainers only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can complete sessions"
        )
    
    completed_booking = session_booking_service.complete_session_booking(db, booking_id, session_notes)
    if not completed_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session booking not found or cannot be completed"
        )
    
    return {"message": "Session completed successfully"}
