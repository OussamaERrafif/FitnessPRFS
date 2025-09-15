from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ProgramTypeEnum(str, Enum):
    STRENGTH_TRAINING = "strength_training"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_BUILDING = "muscle_building"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    SPORTS_SPECIFIC = "sports_specific"
    REHABILITATION = "rehabilitation"
    GENERAL_FITNESS = "general_fitness"


class ProgramDifficultyEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProgramBase(BaseModel):
    """Base program model."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    program_type: ProgramTypeEnum = Field(..., description="Program type")
    difficulty_level: ProgramDifficultyEnum = Field(..., description="Difficulty level")
    duration_weeks: int = Field(..., ge=1, description="Program duration in weeks")
    sessions_per_week: int = Field(..., ge=1, description="Sessions per week")
    goals: Optional[List[str]] = Field(None, description="Program goals")
    target_metrics: Optional[Dict[str, Any]] = Field(None, description="Target improvements")
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)


class ProgramCreate(ProgramBase):
    """Program creation model."""
    client_id: int = Field(..., description="Client ID")
    weekly_schedule: Optional[Dict[str, Any]] = Field(None, description="Weekly workout schedule")
    exercise_list: Optional[List[int]] = Field(None, description="List of exercise IDs")


class ProgramUpdate(BaseModel):
    """Program update model."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    duration_weeks: Optional[int] = Field(None, ge=1)
    sessions_per_week: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None
    current_week: Optional[int] = Field(None, ge=1)
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    sessions_completed: Optional[int] = Field(None, ge=0)
    weekly_schedule: Optional[Dict[str, Any]] = None
    exercise_list: Optional[List[int]] = None
    goals: Optional[List[str]] = None
    target_metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    modifications: Optional[str] = None


class ProgramResponse(ProgramBase):
    """Program response model."""
    id: int
    client_id: int
    trainer_id: int
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    current_week: int
    completion_percentage: float
    sessions_completed: int
    total_sessions: Optional[int]
    weekly_schedule: Optional[Dict[str, Any]]
    exercise_list: Optional[List[int]]
    modifications: Optional[str]
    is_paid: bool
    is_template: bool
    created_from_template_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    client_name: Optional[str] = None
    trainer_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProgramTemplate(BaseModel):
    """Program template model."""
    id: int
    name: str
    description: Optional[str]
    program_type: str
    difficulty_level: str
    duration_weeks: int
    sessions_per_week: int
    weekly_schedule: Optional[Dict[str, Any]]
    exercise_list: Optional[List[int]]
    goals: Optional[List[str]]
    target_metrics: Optional[Dict[str, Any]]
    trainer_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ProgramAssignment(BaseModel):
    """Program assignment model."""
    program_id: int
    client_id: int
    start_date: datetime
    custom_modifications: Optional[str] = None


class WorkoutDay(BaseModel):
    """Individual workout day model."""
    day_number: int
    day_name: str  # "Monday", "Tuesday", etc.
    exercises: List[Dict[str, Any]]
    estimated_duration: Optional[int]  # in minutes
    focus_areas: Optional[List[str]]
    notes: Optional[str]


class WeeklySchedule(BaseModel):
    """Weekly schedule model."""
    week_number: int
    workout_days: List[WorkoutDay]
    rest_days: List[str]
    weekly_goals: Optional[List[str]]
    weekly_notes: Optional[str]


class ProgramExerciseBase(BaseModel):
    """Base program exercise model."""
    exercise_id: int = Field(..., description="Exercise ID")
    week_number: int = Field(..., ge=1, description="Week number")
    day_number: int = Field(..., ge=1, description="Day number")
    order_in_workout: int = Field(..., ge=1, description="Exercise order")
    sets: Optional[int] = Field(None, ge=1)
    reps: Optional[str] = None
    weight_percentage: Optional[float] = Field(None, ge=0, le=100)
    rest_seconds: Optional[int] = Field(None, ge=0)
    duration_seconds: Optional[int] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class ProgramExerciseCreate(ProgramExerciseBase):
    """Program exercise creation model."""
    pass  # program_id will be provided via URL parameter


class ProgramExerciseUpdate(BaseModel):
    """Program exercise update model."""
    sets: Optional[int] = Field(None, ge=1)
    reps: Optional[str] = None
    weight_percentage: Optional[float] = Field(None, ge=0, le=100)
    rest_seconds: Optional[int] = Field(None, ge=0)
    duration_seconds: Optional[int] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class ProgramExerciseResponse(ProgramExerciseBase):
    """Program exercise response model."""
    id: int
    program_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    exercise_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProgramFilter(BaseModel):
    """Program filtering parameters."""
    program_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    status: Optional[str] = None
    client_id: Optional[int] = None
    trainer_id: Optional[int] = None
    is_template: Optional[bool] = None
    duration_weeks_min: Optional[int] = None
    duration_weeks_max: Optional[int] = None
    search: Optional[str] = None


class ProgramProgress(BaseModel):
    """Program progress tracking."""
    program_id: int
    client_id: int
    current_week: int
    total_weeks: int
    completion_percentage: float
    sessions_completed: int
    total_sessions: int
    adherence_rate: float
    missed_sessions: int
    next_workout: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)
