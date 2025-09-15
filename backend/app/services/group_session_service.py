from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException, status
import logging

from app.models.group_session import GroupSession, GroupSessionParticipant, ClientSegment, ClientSegmentAssignment
from app.models.client import Client
from app.models.trainer import Trainer
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class GroupSessionService:
    """Service for managing group fitness sessions."""
    
    @staticmethod
    def create_group_session(db: Session, session_data: Dict[str, Any]) -> GroupSession:
        """Create a new group session."""
        
        # Validate trainer exists
        trainer = db.query(Trainer).filter(Trainer.id == session_data["trainer_id"]).first()
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        
        # Check for scheduling conflicts
        existing_session = db.query(GroupSession).filter(
            and_(
                GroupSession.trainer_id == session_data["trainer_id"],
                GroupSession.scheduled_date == session_data["scheduled_date"],
                GroupSession.is_cancelled == False
            )
        ).first()
        
        if existing_session:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trainer already has a session scheduled at this time"
            )
        
        group_session = GroupSession(**session_data)
        db.add(group_session)
        db.commit()
        db.refresh(group_session)
        
        return group_session
    
    @staticmethod
    def book_group_session(
        db: Session, 
        session_id: int, 
        client_id: int,
        payment_amount: float = 0.0
    ) -> GroupSessionParticipant:
        """Book a client into a group session."""
        
        # Get session and client
        session = db.query(GroupSession).filter(GroupSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group session not found"
            )
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Check if already booked
        existing_booking = db.query(GroupSessionParticipant).filter(
            and_(
                GroupSessionParticipant.group_session_id == session_id,
                GroupSessionParticipant.client_id == client_id,
                GroupSessionParticipant.booking_status.in_(["confirmed", "waitlisted"])
            )
        ).first()
        
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client already booked for this session"
            )
        
        # Check booking deadline
        booking_deadline = session.scheduled_date - timedelta(hours=session.booking_deadline_hours)
        if datetime.utcnow() > booking_deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking deadline has passed"
            )
        
        # Determine booking status
        booking_status = "confirmed"
        waitlist_position = None
        
        if session.current_participants >= session.max_participants:
            if session.allow_waitlist:
                booking_status = "waitlisted"
                # Get current waitlist position
                waitlist_count = db.query(GroupSessionParticipant).filter(
                    and_(
                        GroupSessionParticipant.group_session_id == session_id,
                        GroupSessionParticipant.booking_status == "waitlisted"
                    )
                ).count()
                waitlist_position = waitlist_count + 1
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session is full and waitlist is not allowed"
                )
        
        # Create participant record
        participant = GroupSessionParticipant(
            group_session_id=session_id,
            client_id=client_id,
            booking_status=booking_status,
            amount_paid=payment_amount,
            waitlist_position=waitlist_position
        )
        
        # Update session participant count if confirmed
        if booking_status == "confirmed":
            session.current_participants += 1
            session.total_revenue += payment_amount
        
        db.add(participant)
        db.commit()
        db.refresh(participant)
        
        # Send confirmation notification
        try:
            session_details = {
                "session_title": session.title,
                "session_date": session.scheduled_date.strftime("%Y-%m-%d %H:%M"),
                "location": session.location or "Online",
                "status": booking_status
            }
            notification_service.send_group_session_booking_notification(
                db, client.user_id, session_details
            )
        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {str(e)}")
        
        return participant
    
    @staticmethod
    def cancel_group_session_booking(
        db: Session,
        session_id: int,
        client_id: int,
        cancellation_reason: str = None
    ) -> bool:
        """Cancel a client's booking for a group session."""
        
        participant = db.query(GroupSessionParticipant).filter(
            and_(
                GroupSessionParticipant.group_session_id == session_id,
                GroupSessionParticipant.client_id == client_id,
                GroupSessionParticipant.booking_status.in_(["confirmed", "waitlisted"])
            )
        ).first()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        session = db.query(GroupSession).filter(GroupSession.id == session_id).first()
        was_confirmed = participant.booking_status == "confirmed"
        
        # Update participant status
        participant.booking_status = "cancelled"
        
        # Update session counts
        if was_confirmed:
            session.current_participants -= 1
            session.total_revenue -= participant.amount_paid
            
            # Check if someone on waitlist can be promoted
            GroupSessionService._promote_from_waitlist(db, session_id)
        
        db.commit()
        return True
    
    @staticmethod
    def _promote_from_waitlist(db: Session, session_id: int):
        """Promote the next person from waitlist to confirmed."""
        
        session = db.query(GroupSession).filter(GroupSession.id == session_id).first()
        if session.current_participants >= session.max_participants:
            return
        
        # Get next person on waitlist
        next_participant = db.query(GroupSessionParticipant).filter(
            and_(
                GroupSessionParticipant.group_session_id == session_id,
                GroupSessionParticipant.booking_status == "waitlisted"
            )
        ).order_by(GroupSessionParticipant.waitlist_position).first()
        
        if next_participant:
            next_participant.booking_status = "confirmed"
            next_participant.waitlist_position = None
            next_participant.notified_of_opening = True
            
            session.current_participants += 1
            session.total_revenue += next_participant.amount_paid
            
            # Send notification
            try:
                client = db.query(Client).filter(Client.id == next_participant.client_id).first()
                session_details = {
                    "session_title": session.title,
                    "session_date": session.scheduled_date.strftime("%Y-%m-%d %H:%M"),
                    "location": session.location or "Online"
                }
                notification_service.send_waitlist_promotion_notification(
                    db, client.user_id, session_details
                )
            except Exception as e:
                logger.error(f"Failed to send waitlist promotion notification: {str(e)}")
            
            db.commit()
    
    @staticmethod
    def check_in_participant(db: Session, session_id: int, client_id: int) -> bool:
        """Check in a participant for a group session."""
        
        participant = db.query(GroupSessionParticipant).filter(
            and_(
                GroupSessionParticipant.group_session_id == session_id,
                GroupSessionParticipant.client_id == client_id,
                GroupSessionParticipant.booking_status == "confirmed"
            )
        ).first()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Confirmed booking not found"
            )
        
        participant.checked_in = True
        participant.check_in_time = datetime.utcnow()
        participant.attended = True
        
        db.commit()
        return True


class ClientSegmentService:
    """Service for client segmentation and targeting."""
    
    @staticmethod
    def create_segment(db: Session, segment_data: Dict[str, Any]) -> ClientSegment:
        """Create a new client segment."""
        
        # Check for duplicate names
        existing = db.query(ClientSegment).filter(
            ClientSegment.name == segment_data["name"]
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Segment with this name already exists"
            )
        
        segment = ClientSegment(**segment_data)
        db.add(segment)
        db.commit()
        db.refresh(segment)
        
        # Auto-assign clients if criteria provided
        if segment.auto_update and segment.criteria:
            ClientSegmentService._auto_assign_clients(db, segment)
        
        return segment
    
    @staticmethod
    def assign_client_to_segment(db: Session, client_id: int, segment_id: int, assigned_by: str = "manual") -> ClientSegmentAssignment:
        """Assign a client to a segment."""
        
        # Check if assignment already exists
        existing = db.query(ClientSegmentAssignment).filter(
            and_(
                ClientSegmentAssignment.client_id == client_id,
                ClientSegmentAssignment.segment_id == segment_id,
                ClientSegmentAssignment.is_active == True
            )
        ).first()
        
        if existing:
            return existing
        
        assignment = ClientSegmentAssignment(
            client_id=client_id,
            segment_id=segment_id,
            assigned_by=assigned_by
        )
        
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        return assignment
    
    @staticmethod
    def _auto_assign_clients(db: Session, segment: ClientSegment):
        """Auto-assign clients to segment based on criteria."""
        
        if not segment.criteria:
            return
        
        # This would implement the logic to match clients based on criteria
        # For now, this is a placeholder implementation
        
        # Example criteria matching:
        # {
        #   "fitness_goals": ["weight_loss"],
        #   "activity_level": ["sedentary", "lightly_active"],
        #   "age_range": [25, 45]
        # }
        
        query = db.query(Client)
        
        criteria = segment.criteria
        
        # Apply filters based on criteria
        if "fitness_goals" in criteria:
            # This would need proper JSON querying based on your database
            pass
        
        if "activity_level" in criteria:
            query = query.filter(Client.activity_level.in_(criteria["activity_level"]))
        
        # Get matching clients
        matching_clients = query.all()
        
        # Assign them to the segment
        for client in matching_clients:
            ClientSegmentService.assign_client_to_segment(
                db, client.id, segment.id, "auto"
            )
    
    @staticmethod
    def get_segment_clients(db: Session, segment_id: int) -> List[Client]:
        """Get all clients in a segment."""
        
        return db.query(Client).join(ClientSegmentAssignment).filter(
            and_(
                ClientSegmentAssignment.segment_id == segment_id,
                ClientSegmentAssignment.is_active == True
            )
        ).all()
    
    @staticmethod
    def send_segment_notification(
        db: Session,
        segment_id: int,
        notification_data: Dict[str, Any],
        current_user_id: int
    ) -> int:
        """Send notification to all clients in a segment."""
        
        clients = ClientSegmentService.get_segment_clients(db, segment_id)
        sent_count = 0
        
        for client in clients:
            try:
                notification_service.create_notification(db, {
                    "user_id": client.user_id,
                    **notification_data
                })
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send notification to client {client.id}: {str(e)}")
        
        return sent_count


# Global service instances
group_session_service = GroupSessionService()
client_segment_service = ClientSegmentService()
