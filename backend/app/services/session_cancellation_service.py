from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import logging

from app.models.session_booking import SessionBooking, SessionStatus
from app.models.cancellation import SessionCancellation, CancellationPolicy
from app.models.trainer import Trainer
from app.models.client import Client
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class SessionCancellationService:
    """Service for handling session cancellations and rescheduling."""
    
    @staticmethod
    def cancel_session(
        db: Session,
        session_id: int,
        cancelled_by: str,  # "client", "trainer", "admin"
        cancellation_reason: str,
        current_user_id: int,
        is_emergency: bool = False
    ) -> SessionCancellation:
        """Cancel a session booking."""
        
        # Get the session
        session = db.query(SessionBooking).filter(SessionBooking.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Check if session can be cancelled
        if session.status in [SessionStatus.COMPLETED.value, SessionStatus.CANCELLED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session cannot be cancelled"
            )
        
        # Calculate notice hours
        notice_hours = (session.scheduled_start - datetime.utcnow()).total_seconds() / 3600
        
        # Get cancellation policy
        trainer = db.query(Trainer).filter(Trainer.id == session.trainer_id).first()
        policy = trainer.cancellation_policy if trainer else None
        
        # Determine fee application
        fee_applied = False
        fee_amount = 0.0
        fee_waived = False
        waiver_reason = None
        
        if policy and policy.is_active and policy.auto_apply_policies:
            if cancelled_by == "client":
                if notice_hours < policy.advance_notice_hours:
                    if policy.charge_cancellation_fee:
                        fee_applied = True
                        if policy.cancellation_fee_percentage and session.price:
                            fee_amount = session.price * (policy.cancellation_fee_percentage / 100)
                        else:
                            fee_amount = policy.cancellation_fee_amount
                
                # Check for grace conditions
                if fee_applied and policy.first_time_client_grace:
                    # Check if this is client's first cancellation
                    previous_cancellations = db.query(SessionCancellation).join(SessionBooking).filter(
                        SessionBooking.client_id == session.client_id,
                        SessionCancellation.cancelled_by == "client"
                    ).count()
                    
                    if previous_cancellations == 0:
                        fee_waived = True
                        waiver_reason = "First-time client grace period"
                
                if fee_applied and is_emergency and policy.emergency_exceptions:
                    fee_waived = True
                    waiver_reason = "Emergency cancellation"
        
        # Create cancellation record
        cancellation = SessionCancellation(
            session_booking_id=session_id,
            cancelled_by=cancelled_by,
            cancellation_reason=cancellation_reason,
            is_emergency=is_emergency,
            cancelled_at=datetime.utcnow(),
            notice_hours=notice_hours,
            fee_applied=fee_applied and not fee_waived,
            fee_amount=fee_amount if not fee_waived else 0.0,
            fee_waived=fee_waived,
            waiver_reason=waiver_reason,
            policy_applied=policy is not None
        )
        
        # Update session status
        session.status = SessionStatus.CANCELLED.value
        session.cancelled_at = datetime.utcnow()
        
        db.add(cancellation)
        db.commit()
        db.refresh(cancellation)
        
        # Send notification
        try:
            recipient_id = session.trainer.user_id if cancelled_by == "client" else session.client_id
            notification_service.send_session_cancelled_notification(
                db, recipient_id, {
                    "session_date": session.scheduled_start.strftime("%Y-%m-%d %H:%M"),
                    "cancellation_reason": cancellation_reason,
                    "cancelled_by": cancelled_by,
                    "fee_amount": fee_amount if fee_applied and not fee_waived else 0
                }
            )
        except Exception as e:
            logger.error(f"Failed to send cancellation notification: {str(e)}")
        
        return cancellation
    
    @staticmethod
    def reschedule_session(
        db: Session,
        session_id: int,
        new_start_time: datetime,
        new_end_time: datetime,
        reschedule_reason: str,
        rescheduled_by: str,  # "client", "trainer", "admin"
        current_user_id: int
    ) -> SessionBooking:
        """Reschedule a session to a new time."""
        
        # Get original session
        original_session = db.query(SessionBooking).filter(SessionBooking.id == session_id).first()
        if not original_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Check if session can be rescheduled
        if original_session.status in [SessionStatus.COMPLETED.value, SessionStatus.CANCELLED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session cannot be rescheduled"
            )
        
        # Get cancellation policy for rescheduling rules
        trainer = db.query(Trainer).filter(Trainer.id == original_session.trainer_id).first()
        policy = trainer.cancellation_policy if trainer else None
        
        if policy:
            # Check reschedule limits
            reschedule_count = db.query(SessionBooking).filter(
                SessionBooking.original_session_id == session_id
            ).count()
            
            if reschedule_count >= policy.max_reschedules_per_session:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum reschedules ({policy.max_reschedules_per_session}) exceeded"
                )
            
            # Check advance notice for rescheduling
            notice_hours = (original_session.scheduled_start - datetime.utcnow()).total_seconds() / 3600
            if notice_hours < policy.reschedule_advance_notice_hours:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Reschedule requires {policy.reschedule_advance_notice_hours} hours notice"
                )
        
        # Check trainer availability for new time
        from app.services.session_booking_service import SessionBookingService
        if not SessionBookingService._is_trainer_available(db, original_session.trainer_id, new_start_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trainer not available at requested time"
            )
        
        # Check for conflicts
        duration_minutes = int((new_end_time - new_start_time).total_seconds() / 60)
        existing_booking = SessionBookingService._check_booking_conflict(
            db, original_session.trainer_id, new_start_time, duration_minutes
        )
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Time slot is already booked"
            )
        
        # Mark original session as rescheduled
        original_session.status = SessionStatus.RESCHEDULED.value
        original_session.reschedule_reason = reschedule_reason
        original_session.rescheduled_by = rescheduled_by
        
        # Create new session
        new_session = SessionBooking(
            client_id=original_session.client_id,
            trainer_id=original_session.trainer_id,
            session_type=original_session.session_type,
            title=original_session.title,
            description=original_session.description,
            scheduled_start=new_start_time,
            scheduled_end=new_end_time,
            duration_minutes=duration_minutes,
            location=original_session.location,
            room_number=original_session.room_number,
            online_meeting_url=original_session.online_meeting_url,
            price=original_session.price,
            planned_activities=original_session.planned_activities,
            original_session_id=session_id,
            status=SessionStatus.SCHEDULED.value
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        # Send notifications
        try:
            session_details = {
                "session_time": new_start_time.strftime("%Y-%m-%d %H:%M"),
                "session_type": new_session.session_type,
                "trainer_name": trainer.user.full_name if trainer else "Your trainer",
                "reschedule_reason": reschedule_reason
            }
            
            # Notify the other party
            recipient_id = new_session.trainer.user_id if rescheduled_by == "client" else new_session.client_id
            notification_service.send_session_rescheduled_notification(db, recipient_id, session_details)
            
        except Exception as e:
            logger.error(f"Failed to send reschedule notification: {str(e)}")
        
        return new_session
    
    @staticmethod
    def mark_no_show(
        db: Session,
        session_id: int,
        no_show_party: str,  # "client", "trainer", "both"
        notes: str = None
    ) -> SessionCancellation:
        """Mark a session as no-show and apply penalties."""
        
        session = db.query(SessionBooking).filter(SessionBooking.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Update session status
        session.status = SessionStatus.NO_SHOW.value
        if no_show_party == "client":
            session.client_attended = False
            session.trainer_attended = True
        elif no_show_party == "trainer":
            session.client_attended = True
            session.trainer_attended = False
        else:  # both
            session.client_attended = False
            session.trainer_attended = False
        
        # Apply no-show fee for client no-shows
        fee_applied = False
        fee_amount = 0.0
        
        if "client" in no_show_party:
            trainer = db.query(Trainer).filter(Trainer.id == session.trainer_id).first()
            policy = trainer.cancellation_policy if trainer else None
            
            if policy and policy.charge_no_show_fee:
                fee_applied = True
                if policy.no_show_fee_percentage and session.price:
                    fee_amount = session.price * (policy.no_show_fee_percentage / 100)
                else:
                    fee_amount = policy.no_show_fee_amount
        
        # Create cancellation record for tracking
        cancellation = SessionCancellation(
            session_booking_id=session_id,
            cancelled_by="system",
            cancellation_reason=f"No-show: {no_show_party}",
            cancelled_at=datetime.utcnow(),
            notice_hours=0,
            fee_applied=fee_applied,
            fee_amount=fee_amount,
            policy_applied=True
        )
        
        db.add(cancellation)
        db.commit()
        
        return cancellation
    
    @staticmethod
    def get_cancellation_stats(db: Session, trainer_id: Optional[int] = None) -> Dict[str, Any]:
        """Get cancellation statistics."""
        query = db.query(SessionCancellation)
        
        if trainer_id:
            query = query.join(SessionBooking).filter(SessionBooking.trainer_id == trainer_id)
        
        total_cancellations = query.count()
        client_cancellations = query.filter(SessionCancellation.cancelled_by == "client").count()
        trainer_cancellations = query.filter(SessionCancellation.cancelled_by == "trainer").count()
        no_shows = query.filter(SessionCancellation.cancellation_reason.like("No-show:%")).count()
        
        fees_collected = db.query(func.sum(SessionCancellation.fee_amount)).filter(
            SessionCancellation.fee_applied == True
        ).scalar() or 0
        
        return {
            "total_cancellations": total_cancellations,
            "client_cancellations": client_cancellations,
            "trainer_cancellations": trainer_cancellations,
            "no_shows": no_shows,
            "total_fees_collected": float(fees_collected)
        }


# Global service instance
session_cancellation_service = SessionCancellationService()
