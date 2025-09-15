from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from app.models.session_booking import SessionBooking, SessionStatus
from app.models.client import Client
from app.models.trainer import Trainer, TrainerAvailability
from app.schemas.session_booking import (
    SessionBookingCreate,
    SessionBookingUpdate,
    SessionBookingResponse,
    SessionBookingFilter,
    TimeSlot,
    SessionSummary
)


class SessionBookingService:
    """Service for session booking and scheduling."""
    
    @staticmethod
    def create_session_booking(db: Session, booking_data: SessionBookingCreate) -> SessionBooking:
        """Create a new session booking."""
        # Validate client exists
        client = db.query(Client).filter(Client.id == booking_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Validate trainer exists
        trainer = db.query(Trainer).filter(Trainer.id == booking_data.trainer_id).first()
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        
        # Check trainer availability
        if not SessionBookingService._is_trainer_available(
            db, booking_data.trainer_id, booking_data.scheduled_date
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trainer is not available at the requested time"
            )
        
        # Check for conflicting bookings
        existing_booking = SessionBookingService._check_booking_conflict(
            db, booking_data.trainer_id, booking_data.scheduled_date, booking_data.duration_minutes
        )
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Time slot is already booked"
            )
        
        booking = SessionBooking(**booking_data.model_dump())
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        # Send session confirmation notification
        try:
            from app.services.notification_service import notification_service
            session_details = {
                "session_time": booking.scheduled_start.strftime("%Y-%m-%d %H:%M"),
                "session_type": booking.session_type,
                "trainer_name": booking.trainer.user.full_name or "Your trainer"
            }
            notification_service.send_session_reminder(db, booking.client_id, session_details)
        except Exception as e:
            # Log error but don't fail booking creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send session confirmation notification: {str(e)}")
        
        return booking
    
    @staticmethod
    def get_session_booking_by_id(db: Session, booking_id: int) -> Optional[SessionBooking]:
        """Get session booking by ID."""
        return db.query(SessionBooking).filter(SessionBooking.id == booking_id).first()
    
    @staticmethod
    def get_session_bookings(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[SessionBookingFilter] = None
    ) -> List[SessionBooking]:
        """Get session bookings with optional filtering."""
        query = db.query(SessionBooking)
        
        if filters:
            if filters.client_id:
                query = query.filter(SessionBooking.client_id == filters.client_id)
            
            if filters.trainer_id:
                query = query.filter(SessionBooking.trainer_id == filters.trainer_id)
            
            if filters.status:
                query = query.filter(SessionBooking.status == filters.status)
            
            if filters.start_date:
                query = query.filter(SessionBooking.scheduled_date >= filters.start_date)
            
            if filters.end_date:
                query = query.filter(SessionBooking.scheduled_date <= filters.end_date)
            
            if filters.session_type:
                query = query.filter(SessionBooking.session_type == filters.session_type)
        
        return query.order_by(SessionBooking.scheduled_date).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_session_booking(
        db: Session,
        booking_id: int,
        booking_data: SessionBookingUpdate
    ) -> Optional[SessionBooking]:
        """Update a session booking."""
        booking = db.query(SessionBooking).filter(SessionBooking.id == booking_id).first()
        if not booking:
            return None
        
        update_dict = booking_data.model_dump(exclude_unset=True)
        
        # If rescheduling, check availability
        if 'scheduled_date' in update_dict or 'trainer_id' in update_dict:
            new_trainer_id = update_dict.get('trainer_id', booking.trainer_id)
            new_date = update_dict.get('scheduled_date', booking.scheduled_date)
            new_duration = update_dict.get('duration_minutes', booking.duration_minutes)
            
            # Check trainer availability
            if not SessionBookingService._is_trainer_available(db, new_trainer_id, new_date):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trainer is not available at the requested time"
                )
            
            # Check for conflicts (excluding current booking)
            existing_booking = SessionBookingService._check_booking_conflict(
                db, new_trainer_id, new_date, new_duration, exclude_booking_id=booking_id
            )
            if existing_booking:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Time slot is already booked"
                )
        
        for field, value in update_dict.items():
            setattr(booking, field, value)
        
        booking.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(booking)
        return booking
    
    @staticmethod
    def cancel_session_booking(db: Session, booking_id: int, reason: str = "") -> Optional[SessionBooking]:
        """Cancel a session booking."""
        booking = db.query(SessionBooking).filter(SessionBooking.id == booking_id).first()
        if not booking:
            return None
        
        if booking.status == SessionStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is already cancelled"
            )
        
        booking.status = SessionStatus.CANCELLED
        if reason:
            booking.notes = f"{booking.notes}\nCancellation reason: {reason}" if booking.notes else f"Cancellation reason: {reason}"
        booking.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(booking)
        return booking
    
    @staticmethod
    def confirm_session_booking(db: Session, booking_id: int) -> Optional[SessionBooking]:
        """Confirm a pending session booking."""
        booking = db.query(SessionBooking).filter(SessionBooking.id == booking_id).first()
        if not booking:
            return None
        
        if booking.status != SessionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending sessions can be confirmed"
            )
        
        booking.status = SessionStatus.CONFIRMED
        booking.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(booking)
        return booking
    
    @staticmethod
    def complete_session_booking(
        db: Session, 
        booking_id: int, 
        session_notes: Optional[str] = None
    ) -> Optional[SessionBooking]:
        """Mark a session as completed."""
        booking = db.query(SessionBooking).filter(SessionBooking.id == booking_id).first()
        if not booking:
            return None
        
        if booking.status not in [SessionStatus.CONFIRMED, SessionStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only confirmed or in-progress sessions can be completed"
            )
        
        booking.status = SessionStatus.COMPLETED
        if session_notes:
            booking.notes = f"{booking.notes}\nSession notes: {session_notes}" if booking.notes else f"Session notes: {session_notes}"
        booking.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(booking)
        return booking
    
    @staticmethod
    def get_trainer_schedule(
        db: Session,
        trainer_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[SessionBooking]:
        """Get trainer's schedule for a date range."""
        return db.query(SessionBooking).filter(
            and_(
                SessionBooking.trainer_id == trainer_id,
                SessionBooking.scheduled_date >= start_date,
                SessionBooking.scheduled_date <= end_date,
                SessionBooking.status != SessionStatus.CANCELLED
            )
        ).order_by(SessionBooking.scheduled_date).all()
    
    @staticmethod
    def get_client_sessions(
        db: Session,
        client_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SessionBooking]:
        """Get client's session history."""
        query = db.query(SessionBooking).filter(SessionBooking.client_id == client_id)
        
        if start_date:
            query = query.filter(SessionBooking.scheduled_date >= start_date)
        
        if end_date:
            query = query.filter(SessionBooking.scheduled_date <= end_date)
        
        return query.order_by(desc(SessionBooking.scheduled_date)).all()
    
    @staticmethod
    def get_available_time_slots(
        db: Session,
        trainer_id: int,
        date: datetime.date,
        duration_minutes: int = 60
    ) -> List[TimeSlot]:
        """Get available time slots for a trainer on a specific date."""
        # Get trainer availability for the day
        day_of_week = date.weekday()  # 0 = Monday, 6 = Sunday
        
        availability = db.query(TrainerAvailability).filter(
            and_(
                TrainerAvailability.trainer_id == trainer_id,
                TrainerAvailability.day_of_week == day_of_week,
                TrainerAvailability.is_available == True
            )
        ).first()
        
        if not availability:
            return []
        
        # Get existing bookings for the date
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)
        
        existing_bookings = db.query(SessionBooking).filter(
            and_(
                SessionBooking.trainer_id == trainer_id,
                SessionBooking.scheduled_date >= start_of_day,
                SessionBooking.scheduled_date < end_of_day,
                SessionBooking.status != SessionStatus.CANCELLED
            )
        ).order_by(SessionBooking.scheduled_date).all()
        
        # Generate available time slots
        available_slots = []
        
        # Convert availability times to datetime
        start_time = datetime.combine(date, availability.start_time)
        end_time = datetime.combine(date, availability.end_time)
        
        current_time = start_time
        slot_duration = timedelta(minutes=duration_minutes)
        
        while current_time + slot_duration <= end_time:
            # Check if this slot conflicts with existing bookings
            slot_end = current_time + slot_duration
            
            is_available = True
            for booking in existing_bookings:
                booking_end = booking.scheduled_date + timedelta(minutes=booking.duration_minutes)
                
                # Check for overlap
                if (current_time < booking_end and slot_end > booking.scheduled_date):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(TimeSlot(
                    start_time=current_time.time(),
                    end_time=slot_end.time(),
                    is_available=True
                ))
            
            # Move to next slot (increment by 30 minutes for flexibility)
            current_time += timedelta(minutes=30)
        
        return available_slots
    
    @staticmethod
    def _is_trainer_available(db: Session, trainer_id: int, scheduled_date: datetime) -> bool:
        """Check if trainer is available at the specified time."""
        day_of_week = scheduled_date.weekday()
        time = scheduled_date.time()
        
        availability = db.query(TrainerAvailability).filter(
            and_(
                TrainerAvailability.trainer_id == trainer_id,
                TrainerAvailability.day_of_week == day_of_week,
                TrainerAvailability.is_available == True,
                TrainerAvailability.start_time <= time,
                TrainerAvailability.end_time >= time
            )
        ).first()
        
        return availability is not None
    
    @staticmethod
    def _check_booking_conflict(
        db: Session,
        trainer_id: int,
        scheduled_date: datetime,
        duration_minutes: int,
        exclude_booking_id: Optional[int] = None
    ) -> Optional[SessionBooking]:
        """Check for booking conflicts."""
        session_end = scheduled_date + timedelta(minutes=duration_minutes)
        
        query = db.query(SessionBooking).filter(
            and_(
                SessionBooking.trainer_id == trainer_id,
                SessionBooking.status != SessionStatus.CANCELLED,
                # Check for overlap
                or_(
                    and_(
                        SessionBooking.scheduled_date <= scheduled_date,
                        func.datetime(
                            SessionBooking.scheduled_date,
                            '+' + func.cast(SessionBooking.duration_minutes, db.String) + ' minutes'
                        ) > scheduled_date
                    ),
                    and_(
                        SessionBooking.scheduled_date < session_end,
                        SessionBooking.scheduled_date >= scheduled_date
                    )
                )
            )
        )
        
        if exclude_booking_id:
            query = query.filter(SessionBooking.id != exclude_booking_id)
        
        return query.first()
    
    @staticmethod
    def get_session_summary(db: Session, booking_id: int) -> Optional[SessionSummary]:
        """Get session summary information."""
        booking = db.query(SessionBooking).filter(SessionBooking.id == booking_id).first()
        if not booking:
            return None
        
        # Get client and trainer info
        client = db.query(Client).filter(Client.id == booking.client_id).first()
        trainer = db.query(Trainer).filter(Trainer.id == booking.trainer_id).first()
        
        return SessionSummary(
            booking_id=booking.id,
            client_name=client.user.full_name if client and client.user else "Unknown Client",
            trainer_name=trainer.user.full_name if trainer and trainer.user else "Unknown Trainer",
            session_date=booking.scheduled_date.date(),
            session_time=booking.scheduled_date.time(),
            duration_minutes=booking.duration_minutes,
            session_type=booking.session_type,
            status=booking.status,
            location=booking.location,
            notes=booking.notes
        )


# Global session booking service instance
session_booking_service = SessionBookingService()
