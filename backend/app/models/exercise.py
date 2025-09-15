from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class ExerciseCategory(PyEnum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    SPORTS = "sports"
    FUNCTIONAL = "functional"
    REHABILITATION = "rehabilitation"


class MuscleGroup(PyEnum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    FOREARMS = "forearms"
    ABS = "abs"
    OBLIQUES = "obliques"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    FULL_BODY = "full_body"
    CARDIO = "cardio"


class EquipmentType(PyEnum):
    BODYWEIGHT = "bodyweight"
    DUMBBELLS = "dumbbells"
    BARBELL = "barbell"
    KETTLEBELL = "kettlebell"
    RESISTANCE_BANDS = "resistance_bands"
    CABLE_MACHINE = "cable_machine"
    CARDIO_MACHINE = "cardio_machine"
    YOGA_MAT = "yoga_mat"
    MEDICINE_BALL = "medicine_ball"
    SUSPENSION_TRAINER = "suspension_trainer"
    OTHER = "other"


class ExerciseType(PyEnum):
    REPS = "reps"
    TIME = "time"
    DISTANCE = "distance"
    REPS_AND_WEIGHT = "reps_and_weight"
    TIME_AND_INTENSITY = "time_and_intensity"
    COMPOUND = "compound"
    CARDIO = "cardio"
    BODYWEIGHT = "bodyweight"


class DifficultyLevel(PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Exercise(Base):
    """Exercise model for storing exercise information."""
    
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    # Classification
    category = Column(String(50), nullable=False)  # ExerciseCategory enum as string
    muscle_groups = Column(Text, nullable=True)  # JSON string of muscle groups
    equipment_needed = Column(Text, nullable=True)  # JSON string of equipment
    difficulty_level = Column(String(50), nullable=True)  # DifficultyLevel enum as string
    
    # Media
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    animation_url = Column(String(500), nullable=True)
    
    # Exercise details
    default_sets = Column(Integer, nullable=True)
    default_reps = Column(String(50), nullable=True)  # "8-12" or "30 seconds"
    default_weight = Column(Float, nullable=True)
    default_duration = Column(Integer, nullable=True)  # in seconds
    rest_time = Column(Integer, nullable=True)  # in seconds
    
    # Metrics
    calories_per_minute = Column(Float, nullable=True)
    
    # Safety and tips
    safety_tips = Column(Text, nullable=True)
    common_mistakes = Column(Text, nullable=True)
    alternatives = Column(Text, nullable=True)  # JSON string of alternative exercises
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    # Creator (for custom exercises)
    created_by_trainer_id = Column(Integer, nullable=True)  # If created by specific trainer
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress_logs = relationship("ProgressLog", back_populates="exercise")
    
    def __repr__(self):
        return f"<Exercise(id={self.id}, name='{self.name}', category='{self.category}')>"
