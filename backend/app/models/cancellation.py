from datetime import datetime, timedelta
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class CancellationPolicy(Base):
    """Cancellation policy model for trainers."""
    
    __tablename__ = "cancellation_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False, unique=True)
    
    # Cancellation rules
    advance_notice_hours = Column(Integer, default=24)  # Hours notice required
    allow_client_cancellation = Column(Boolean, default=True)
    allow_client_reschedule = Column(Boolean, default=True)
    
    # Penalty settings
    charge_cancellation_fee = Column(Boolean, default=False)
    cancellation_fee_amount = Column(Float, default=0.0)
    cancellation_fee_percentage = Column(Float, nullable=True)  # % of session price
    
    # No-show policy
    charge_no_show_fee = Column(Boolean, default=True)
    no_show_fee_amount = Column(Float, default=0.0)
    no_show_fee_percentage = Column(Float, default=100.0)  # % of session price
    
    # Rescheduling limits
    max_reschedules_per_session = Column(Integer, default=2)
    reschedule_advance_notice_hours = Column(Integer, default=12)
    
    # Grace periods
    first_time_client_grace = Column(Boolean, default=True)  # Waive fees for first-time clients
    emergency_exceptions = Column(Boolean, default=True)  # Allow emergency cancellations
    
    # Policy text
    policy_description = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    auto_apply_policies = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trainer = relationship("Trainer", back_populates="cancellation_policy")
    
    def __repr__(self):
        return f"<CancellationPolicy(id={self.id}, trainer_id={self.trainer_id})>"


class SessionCancellation(Base):
    """Track session cancellations and their reasons."""
    
    __tablename__ = "session_cancellations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_booking_id = Column(Integer, ForeignKey("session_bookings.id"), nullable=False)
    
    # Cancellation details
    cancelled_by = Column(String(20), nullable=False)  # "client", "trainer", "system"
    cancellation_reason = Column(String(500), nullable=True)
    is_emergency = Column(Boolean, default=False)
    
    # Timing
    cancelled_at = Column(DateTime, nullable=False)
    notice_hours = Column(Float, nullable=True)  # Hours of notice given
    
    # Financial impact
    fee_applied = Column(Boolean, default=False)
    fee_amount = Column(Float, default=0.0)
    fee_waived = Column(Boolean, default=False)
    waiver_reason = Column(String(255), nullable=True)
    
    # Rescheduling
    is_rescheduled = Column(Boolean, default=False)
    new_session_booking_id = Column(Integer, nullable=True)
    
    # System tracking
    policy_applied = Column(Boolean, default=False)
    manual_override = Column(Boolean, default=False)
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session_booking = relationship("SessionBooking")
    
    def __repr__(self):
        return f"<SessionCancellation(id={self.id}, session_id={self.session_booking_id}, cancelled_by='{self.cancelled_by}')>"


class TrainerAvailabilitySlot(Base):
    """Trainer availability schedule slots."""
    
    __tablename__ = "trainer_availability_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Day and time
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String(5), nullable=False)  # HH:MM format
    end_time = Column(String(5), nullable=False)    # HH:MM format
    
    # Availability details
    is_available = Column(Boolean, default=True)
    max_sessions = Column(Integer, default=1)  # Max sessions in this time slot
    session_duration_minutes = Column(Integer, default=60)
    
    # Special dates
    specific_date = Column(DateTime, nullable=True)  # For one-time availability changes
    is_recurring = Column(Boolean, default=True)    # If this applies weekly
    
    # Settings
    is_active = Column(Boolean, default=True)
    allows_booking = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trainer = relationship("Trainer", back_populates="availability_slots")
    
    def __repr__(self):
        return f"<TrainerAvailabilitySlot(id={self.id}, trainer_id={self.trainer_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time})>"
