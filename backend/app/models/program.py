from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class ProgramType(PyEnum):
    STRENGTH_TRAINING = "strength_training"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_BUILDING = "muscle_building"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    SPORTS_SPECIFIC = "sports_specific"
    REHABILITATION = "rehabilitation"
    GENERAL_FITNESS = "general_fitness"


class ProgramDifficulty(PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProgramStatus(PyEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Program(Base):
    """Training program model."""
    
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Program details
    program_type = Column(String(50), nullable=False)  # ProgramType enum as string
    difficulty_level = Column(String(50), nullable=False)  # ProgramDifficulty enum as string
    duration_weeks = Column(Integer, nullable=False)  # Program duration in weeks
    sessions_per_week = Column(Integer, nullable=False)
    
    # Assignment
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Status and dates
    status = Column(String(50), default=ProgramStatus.ACTIVE.value)  # ProgramStatus enum as string
    is_active = Column(Boolean, default=True)  # Whether the program is active
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    
    # Progress tracking
    current_week = Column(Integer, default=1)
    completion_percentage = Column(Float, default=0.0)
    sessions_completed = Column(Integer, default=0)
    total_sessions = Column(Integer, nullable=True)
    
    # Program structure (JSON)
    weekly_schedule = Column(Text, nullable=True)  # JSON structure of weekly workouts
    exercise_list = Column(Text, nullable=True)  # JSON list of exercises used
    
    # Goals and targets
    goals = Column(Text, nullable=True)  # JSON string of specific goals
    target_metrics = Column(Text, nullable=True)  # JSON string of target improvements
    
    # Notes and customization
    notes = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    modifications = Column(Text, nullable=True)  # Any modifications made to the program
    
    # Pricing (if applicable)
    price = Column(Float, nullable=True)
    is_paid = Column(Boolean, default=False)
    
    # Template information
    is_template = Column(Boolean, default=False)  # If this is a reusable template
    created_from_template_id = Column(Integer, nullable=True)  # If created from a template
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="programs")
    trainer = relationship("Trainer", back_populates="programs")
    
    def __repr__(self):
        return f"<Program(id={self.id}, name='{self.name}', client_id={self.client_id})>"
    
    @property
    def goals_list(self):
        """Return goals as a list, parsing from JSON if needed."""
        if self.goals:
            import json
            try:
                return json.loads(self.goals)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @property 
    def exercise_list_ids(self):
        """Return exercise list as a list of integers, parsing from JSON if needed."""
        if self.exercise_list:
            import json
            try:
                return json.loads(self.exercise_list)
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class ProgramExercise(Base):
    """Program exercise association model."""
    
    __tablename__ = "program_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # Exercise parameters for this program
    week_number = Column(Integer, nullable=False)
    day_number = Column(Integer, nullable=False)
    order_in_workout = Column(Integer, nullable=False)
    
    # Prescribed parameters
    sets = Column(Integer, nullable=True)
    reps = Column(String(50), nullable=True)  # "8-12" or "10"
    weight_percentage = Column(Float, nullable=True)  # Percentage of 1RM
    rest_seconds = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # For timed exercises
    distance = Column(Float, nullable=True)  # For distance-based exercises
    
    # Instructions
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProgramExercise(id={self.id}, program_id={self.program_id}, exercise_id={self.exercise_id})>"
