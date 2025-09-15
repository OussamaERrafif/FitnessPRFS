from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class WorkoutType(PyEnum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    SPORTS = "sports"
    MIXED = "mixed"


class IntensityLevel(PyEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    MAXIMUM = "maximum"


class LogType(PyEnum):
    WORKOUT = "workout"
    MEASUREMENT = "measurement"
    ACHIEVEMENT = "achievement"
    GOAL = "goal"


class ProgressType(PyEnum):
    WEIGHT = "weight"
    BODY_FAT = "body_fat"
    MUSCLE_MASS = "muscle_mass"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"


class ProgressLog(Base):
    """Progress log model for tracking workout progress and PRs."""
    
    __tablename__ = "progress_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # Workout session info
    workout_date = Column(DateTime, nullable=False, index=True)
    log_type = Column(String(50), nullable=False, default="workout")  # LogType enum as string
    workout_type = Column(String(50), nullable=True)  # WorkoutType enum as string
    
    # Exercise performance
    sets = Column(Integer, nullable=True)
    reps = Column(String(100), nullable=True)  # Can be "10" or "10,8,6" for multiple sets
    weight = Column(Float, nullable=True)  # in kg or lbs
    distance = Column(Float, nullable=True)  # in km or miles
    duration = Column(Integer, nullable=True)  # in seconds
    calories_burned = Column(Float, nullable=True)
    
    # Performance metrics
    max_weight = Column(Float, nullable=True)  # Personal record for weight
    max_reps = Column(Integer, nullable=True)  # Personal record for reps
    best_time = Column(Integer, nullable=True)  # Best time in seconds
    
    # Subjective measures
    intensity_level = Column(String(50), nullable=True)  # IntensityLevel enum as string
    perceived_exertion = Column(Integer, nullable=True)  # RPE scale 1-10
    energy_level_before = Column(Integer, nullable=True)  # Scale 1-10
    energy_level_after = Column(Integer, nullable=True)  # Scale 1-10
    
    # Notes and feedback
    notes = Column(Text, nullable=True)
    form_rating = Column(Integer, nullable=True)  # Self-rated form 1-10
    
    # Context
    location = Column(String(255), nullable=True)  # Gym name or "Home"
    weather = Column(String(100), nullable=True)  # For outdoor activities
    
    # Progress indicators
    is_personal_record = Column(Boolean, default=False)
    improvement_from_last = Column(Float, nullable=True)  # Percentage improvement
    
    # Body measurements (optional, for tracking body composition)
    body_weight = Column(Float, nullable=True)  # User's body weight on this day
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress_logs")
    exercise = relationship("Exercise", back_populates="progress_logs")
    
    def __repr__(self):
        return f"<ProgressLog(id={self.id}, user_id={self.user_id}, exercise_id={self.exercise_id}, date={self.workout_date})>"
