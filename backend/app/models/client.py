from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class ActivityLevel(PyEnum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class FitnessGoal(PyEnum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH_GAIN = "strength_gain"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"
    SPORTS_PERFORMANCE = "sports_performance"


class Client(Base):
    """Client profile extending the User model."""
    
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Personal information
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)  # in cm
    fitness_level = Column(String(50), nullable=True)  # Beginner, Intermediate, Advanced
    
    # Fitness profile
    current_weight = Column(Float, nullable=True)  # in kg
    target_weight = Column(Float, nullable=True)  # in kg
    activity_level = Column(String(50), nullable=True)  # ActivityLevel enum as string
    # Use JSON for list-like fields
    fitness_goals = Column(JSON().with_variant(SQLITE_JSON, 'sqlite'), nullable=True)
    
    # Health information
    medical_conditions = Column(JSON().with_variant(SQLITE_JSON, 'sqlite'), nullable=True)
    injuries = Column(JSON().with_variant(SQLITE_JSON, 'sqlite'), nullable=True)
    medications = Column(JSON().with_variant(SQLITE_JSON, 'sqlite'), nullable=True)
    
    # Training preferences
    preferred_workout_days = Column(JSON().with_variant(SQLITE_JSON, 'sqlite'), nullable=True)
    preferred_workout_time = Column(String(50), nullable=True)
    workout_experience = Column(String(50), nullable=True)  # Beginner, Intermediate, Advanced
    
    # Trainer assignment
    assigned_trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    
    # PIN for access control
    pin = Column(String(6), nullable=True, unique=True)
    pin_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Subscription/membership
    membership_type = Column(String(100), nullable=True)
    membership_start_date = Column(DateTime, nullable=True)
    membership_end_date = Column(DateTime, nullable=True)
    is_membership_active = Column(Boolean, default=False)
    
    # Emergency contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="client_profile")
    assigned_trainer = relationship("Trainer", back_populates="clients")
    programs = relationship("Program", back_populates="client")
    meal_plans = relationship("MealPlan", back_populates="client")
    
    def __repr__(self):
        return f"<Client(id={self.id}, user_id={self.user_id})>"
