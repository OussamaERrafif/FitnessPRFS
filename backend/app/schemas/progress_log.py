from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ProgressLogBase(BaseModel):
    """Base progress log model."""
    exercise_id: int = Field(..., description="Exercise ID")
    workout_date: datetime = Field(..., description="Workout date and time")
    log_type: Optional[str] = Field(default="workout", description="Type of log entry")
    workout_type: Optional[str] = None
    sets: Optional[int] = Field(None, ge=1)
    reps: Optional[str] = None
    weight: Optional[float] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    calories_burned: Optional[float] = Field(None, ge=0)
    intensity_level: Optional[str] = None
    perceived_exertion: Optional[int] = Field(None, ge=1, le=10)
    energy_level_before: Optional[int] = Field(None, ge=1, le=10)
    energy_level_after: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    form_rating: Optional[int] = Field(None, ge=1, le=10)
    location: Optional[str] = None
    weather: Optional[str] = None
    body_weight: Optional[float] = Field(None, ge=0)
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    muscle_mass: Optional[float] = Field(None, ge=0)


class ProgressLogCreate(ProgressLogBase):
    """Progress log creation model."""
    user_id: int = Field(..., description="User ID (client)")


class ProgressLogUpdate(BaseModel):
    """Progress log update model."""
    sets: Optional[int] = Field(None, ge=1)
    reps: Optional[str] = None
    weight: Optional[float] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=0)
    calories_burned: Optional[float] = Field(None, ge=0)
    intensity_level: Optional[str] = None
    perceived_exertion: Optional[int] = Field(None, ge=1, le=10)
    energy_level_before: Optional[int] = Field(None, ge=1, le=10)
    energy_level_after: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    form_rating: Optional[int] = Field(None, ge=1, le=10)
    body_weight: Optional[float] = Field(None, ge=0)
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    muscle_mass: Optional[float] = Field(None, ge=0)


class ProgressLogResponse(ProgressLogBase):
    """Progress log response model."""
    id: int
    user_id: int
    max_weight: Optional[float] = None
    max_reps: Optional[int] = None
    best_time: Optional[int] = None
    is_personal_record: Optional[bool] = False
    improvement_from_last: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Related data
    exercise_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class PersonalRecord(BaseModel):
    """Personal record model."""
    exercise_id: int
    exercise_name: str
    record_type: str  # "weight", "reps", "time", "distance"
    record_value: float
    record_date: datetime
    previous_record: Optional[float]
    improvement_percentage: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)


class WorkoutSummary(BaseModel):
    """Workout session summary."""
    date: datetime
    total_exercises: int
    total_duration: int  # in seconds
    total_calories: Optional[float]
    average_intensity: Optional[float]
    exercises_performed: List[str]
    personal_records: int
    
    model_config = ConfigDict(from_attributes=True)


class ProgressLogFilter(BaseModel):
    """Progress log filtering parameters."""
    exercise_id: Optional[int] = None
    log_type: Optional[str] = None
    workout_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    intensity_level: Optional[str] = None
    is_personal_record: Optional[bool] = None


class ProgressStats(BaseModel):
    """Progress statistics model."""
    total_workouts: int
    total_exercises_performed: int
    total_duration_hours: float
    total_calories_burned: Optional[float]
    personal_records_count: int
    current_streak_days: int
    average_workouts_per_week: float
    most_performed_exercise: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class WeightProgressChart(BaseModel):
    """Weight progress chart data."""
    dates: List[datetime]
    weights: List[float]
    body_fat_percentages: List[Optional[float]]
    muscle_masses: List[Optional[float]]
    
    model_config = ConfigDict(from_attributes=True)
