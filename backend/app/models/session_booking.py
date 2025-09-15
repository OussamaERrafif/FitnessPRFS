from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class SessionType(PyEnum):
    PERSONAL_TRAINING = "personal_training"
    GROUP_TRAINING = "group_training"
    CONSULTATION = "consultation"
    ASSESSMENT = "assessment"
    FOLLOW_UP = "follow_up"
    ONLINE_SESSION = "online_session"


class SessionStatus(PyEnum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class SessionBooking(Base):
    """Session booking model for trainer-client appointments."""
    
    __tablename__ = "session_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Participants
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # References User directly
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Session details
    session_type = Column(String(50), nullable=False)  # SessionType enum as string
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_start = Column(DateTime, nullable=False, index=True)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    
    # Status
    status = Column(String(50), default=SessionStatus.SCHEDULED.value)  # SessionStatus enum as string
    
    # Location
    location = Column(String(255), nullable=True)  # Gym name, address, or "Online"
    room_number = Column(String(50), nullable=True)
    online_meeting_url = Column(String(500), nullable=True)
    online_meeting_id = Column(String(100), nullable=True)
    
    # Pricing
    price = Column(Float, nullable=True)
    is_paid = Column(Boolean, default=False)
    payment_method = Column(String(50), nullable=True)
    
    # Session content
    planned_activities = Column(Text, nullable=True)  # JSON string of planned exercises/activities
    actual_activities = Column(Text, nullable=True)  # JSON string of what was actually done
    
    # Notes and feedback
    trainer_notes_before = Column(Text, nullable=True)
    trainer_notes_after = Column(Text, nullable=True)
    client_notes = Column(Text, nullable=True)
    
    # Session outcomes
    goals_achieved = Column(Text, nullable=True)  # JSON string
    homework_assigned = Column(Text, nullable=True)
    next_session_recommendations = Column(Text, nullable=True)
    
    # Ratings and feedback
    client_rating = Column(Integer, nullable=True)  # 1-5 stars
    trainer_rating = Column(Integer, nullable=True)  # 1-5 stars
    client_feedback = Column(Text, nullable=True)
    trainer_feedback = Column(Text, nullable=True)
    
    # Attendance tracking
    client_attended = Column(Boolean, nullable=True)
    trainer_attended = Column(Boolean, nullable=True)
    
    # Rescheduling
    original_session_id = Column(Integer, nullable=True)  # If this is a rescheduled session
    reschedule_reason = Column(String(255), nullable=True)
    rescheduled_by = Column(String(50), nullable=True)  # "client" or "trainer"
    
    # Notifications
    reminder_sent = Column(Boolean, default=False)
    confirmation_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("User", back_populates="session_bookings")
    trainer = relationship("Trainer", back_populates="session_bookings")
    
    def __repr__(self):
        return f"<SessionBooking(id={self.id}, client_id={self.client_id}, trainer_id={self.trainer_id}, start={self.scheduled_start})>"
