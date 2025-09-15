from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class GroupSessionType(PyEnum):
    FITNESS_CLASS = "fitness_class"
    BOOTCAMP = "bootcamp"
    YOGA = "yoga"
    PILATES = "pilates"
    CARDIO = "cardio"
    STRENGTH = "strength"
    HIIT = "hiit"
    DANCE = "dance"
    MARTIAL_ARTS = "martial_arts"
    SPORTS = "sports"
    REHABILITATION = "rehabilitation"
    SENIOR_FITNESS = "senior_fitness"


class GroupSession(Base):
    """Group fitness session model."""
    
    __tablename__ = "group_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Session details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    session_type = Column(String(50), nullable=False)  # GroupSessionType enum as string
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    
    # Capacity
    max_participants = Column(Integer, default=10)
    min_participants = Column(Integer, default=1)
    current_participants = Column(Integer, default=0)
    
    # Location
    location = Column(String(255), nullable=True)
    room_number = Column(String(50), nullable=True)
    online_meeting_url = Column(String(500), nullable=True)
    is_online = Column(Boolean, default=False)
    
    # Pricing
    price_per_person = Column(Float, nullable=True)
    total_revenue = Column(Float, default=0.0)
    
    # Requirements
    difficulty_level = Column(String(50), nullable=True)
    age_restrictions = Column(String(100), nullable=True)
    equipment_required = Column(JSON, nullable=True)
    prerequisites = Column(Text, nullable=True)
    
    # Session status
    status = Column(String(50), default="scheduled")  # scheduled, confirmed, cancelled, completed
    is_cancelled = Column(Boolean, default=False)
    cancellation_reason = Column(String(255), nullable=True)
    
    # Booking settings
    allow_booking = Column(Boolean, default=True)
    booking_deadline_hours = Column(Integer, default=2)  # Hours before session
    allow_waitlist = Column(Boolean, default=True)
    
    # Content
    session_plan = Column(JSON, nullable=True)  # Detailed workout plan
    equipment_list = Column(JSON, nullable=True)
    warm_up_plan = Column(Text, nullable=True)
    main_workout_plan = Column(Text, nullable=True)
    cool_down_plan = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trainer = relationship("Trainer", back_populates="group_sessions")
    participants = relationship("GroupSessionParticipant", back_populates="group_session")
    
    def __repr__(self):
        return f"<GroupSession(id={self.id}, title='{self.title}', date={self.scheduled_date})>"


class GroupSessionParticipant(Base):
    """Group session participant tracking."""
    
    __tablename__ = "group_session_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    group_session_id = Column(Integer, ForeignKey("group_sessions.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Booking details
    booked_at = Column(DateTime, nullable=False, default=func.now())
    booking_status = Column(String(50), default="confirmed")  # confirmed, waitlisted, cancelled, attended, no_show
    
    # Payment
    amount_paid = Column(Float, default=0.0)
    payment_status = Column(String(50), default="pending")  # pending, paid, refunded
    payment_method = Column(String(50), nullable=True)
    
    # Attendance
    checked_in = Column(Boolean, default=False)
    check_in_time = Column(DateTime, nullable=True)
    attended = Column(Boolean, nullable=True)
    
    # Waitlist
    waitlist_position = Column(Integer, nullable=True)
    notified_of_opening = Column(Boolean, default=False)
    
    # Feedback
    rating = Column(Integer, nullable=True)  # 1-5 stars
    feedback = Column(Text, nullable=True)
    
    # Special requirements
    dietary_restrictions = Column(JSON, nullable=True)
    medical_conditions = Column(Text, nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    group_session = relationship("GroupSession", back_populates="participants")
    client = relationship("Client")
    
    def __repr__(self):
        return f"<GroupSessionParticipant(id={self.id}, session_id={self.group_session_id}, client_id={self.client_id})>"


class ClientSegment(Base):
    """Client segmentation for targeted communications and programs."""
    
    __tablename__ = "client_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Segment criteria (JSON filters)
    criteria = Column(JSON, nullable=True)  # Store filter conditions
    
    # Segment properties
    color_code = Column(String(7), nullable=True)  # Hex color for UI
    icon = Column(String(50), nullable=True)
    priority = Column(Integer, default=0)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_system_segment = Column(Boolean, default=False)  # Cannot be deleted
    auto_update = Column(Boolean, default=True)  # Auto-add clients matching criteria
    
    # Created by
    created_by_trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by_trainer = relationship("Trainer")
    client_assignments = relationship("ClientSegmentAssignment", back_populates="segment")
    
    def __repr__(self):
        return f"<ClientSegment(id={self.id}, name='{self.name}')>"


class ClientSegmentAssignment(Base):
    """Assignment of clients to segments."""
    
    __tablename__ = "client_segment_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("client_segments.id"), nullable=False)
    
    # Assignment details
    assigned_at = Column(DateTime, nullable=False, default=func.now())
    assigned_by = Column(String(50), nullable=True)  # "manual", "auto", "import"
    is_active = Column(Boolean, default=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client")
    segment = relationship("ClientSegment", back_populates="client_assignments")
    
    def __repr__(self):
        return f"<ClientSegmentAssignment(id={self.id}, client_id={self.client_id}, segment_id={self.segment_id})>"


class TrainerNote(Base):
    """Trainer notes about clients."""
    
    __tablename__ = "trainer_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Note details
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), nullable=True)  # general, progress, concern, achievement, etc.
    
    # Priority and visibility
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    is_private = Column(Boolean, default=False)  # Only visible to trainer
    is_flagged = Column(Boolean, default=False)  # Important notes
    
    # Categories/Tags
    tags = Column(JSON, nullable=True)  # List of tags
    category = Column(String(100), nullable=True)
    
    # Related entities
    session_id = Column(Integer, ForeignKey("session_bookings.id"), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trainer = relationship("Trainer")
    client = relationship("Client")
    session = relationship("SessionBooking")
    program = relationship("Program")
    
    def __repr__(self):
        return f"<TrainerNote(id={self.id}, trainer_id={self.trainer_id}, client_id={self.client_id})>"
