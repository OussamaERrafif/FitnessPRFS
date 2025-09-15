from datetime import datetime, time
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class Trainer(Base):
    """Trainer profile extending the User model."""
    
    __tablename__ = "trainers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Professional information
    certification = Column(String(255), nullable=True)
    specializations = Column(Text, nullable=True)  # JSON string of specializations
    years_of_experience = Column(Integer, nullable=True)
    experience_years = Column(Integer, nullable=True)  # Alias for compatibility
    education = Column(Text, nullable=True)
    
    # Business information
    hourly_rate = Column(Float, nullable=True)  # Price per hour
    bio = Column(Text, nullable=True)
    services_offered = Column(Text, nullable=True)  # JSON string
    
    # Availability
    available_days = Column(String(100), nullable=True)  # JSON string
    available_hours = Column(String(100), nullable=True)  # JSON string
    timezone = Column(String(50), nullable=True)
    
    # Professional status
    is_verified = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Rating and reviews
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Location
    location = Column(String(255), nullable=True)  # Combined location field
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Online/offline training
    offers_online_training = Column(Boolean, default=False)
    offers_in_person_training = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trainer_profile")
    clients = relationship("Client", back_populates="assigned_trainer")
    programs = relationship("Program", back_populates="trainer")
    session_bookings = relationship("SessionBooking", back_populates="trainer")
    certifications = relationship("TrainerCertification", back_populates="trainer", cascade="all, delete-orphan")
    availability = relationship("TrainerAvailability", back_populates="trainer", cascade="all, delete-orphan")
    availability_slots = relationship("TrainerAvailabilitySlot", back_populates="trainer", cascade="all, delete-orphan")
    cancellation_policy = relationship("CancellationPolicy", back_populates="trainer", uselist=False)
    group_sessions = relationship("GroupSession", back_populates="trainer")
    
    def __repr__(self):
        return f"<Trainer(id={self.id}, user_id={self.user_id})>"


class TrainerCertification(Base):
    """Trainer certifications and qualifications."""
    
    __tablename__ = "trainer_certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Certification details
    name = Column(String(200), nullable=False)
    issuing_organization = Column(String(200), nullable=True)
    certification_number = Column(String(100), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    
    # Status
    is_current = Column(Boolean, default=True)
    
    # Relationships
    trainer = relationship("Trainer", back_populates="certifications")
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TrainerAvailability(Base):
    """Trainer weekly availability schedule."""
    
    __tablename__ = "trainer_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Schedule details
    day_of_week = Column(Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    trainer = relationship("Trainer", back_populates="availability")
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
