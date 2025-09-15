from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
import json


class ExerciseBase(BaseModel):
    """Base exercise model."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    instructions: Optional[List[str]] = Field(None, description="Step-by-step instructions")
    category: Optional[str] = Field(None, description="Exercise category")
    muscle_groups: Optional[List[str]] = Field(None, description="Target muscle groups")
    equipment: Optional[str] = Field(None, description="Required equipment")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    tips: Optional[List[str]] = Field(None, description="Exercise tips")
    default_sets: Optional[int] = Field(None, ge=1)
    default_reps: Optional[str] = None
    default_weight: Optional[float] = Field(None, ge=0)
    default_duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    rest_time: Optional[int] = Field(None, ge=0, description="Rest time in seconds")
    calories_per_minute: Optional[float] = Field(None, ge=0)
    safety_tips: Optional[str] = None
    common_mistakes: Optional[str] = None
    alternatives: Optional[List[str]] = Field(None, description="Alternative exercises")


class ExerciseCreateInternal(BaseModel):
    """Internal exercise creation model for database storage."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None  # JSON string in database
    category: Optional[str] = Field(None, description="Exercise category")
    muscle_groups: Optional[str] = None  # JSON string in database
    equipment: Optional[str] = Field(None, description="Required equipment")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    tips: Optional[str] = None  # JSON string in database
    default_sets: Optional[int] = Field(None, ge=1)
    default_reps: Optional[str] = None
    default_weight: Optional[float] = Field(None, ge=0)
    default_duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    rest_time: Optional[int] = Field(None, ge=0, description="Rest time in seconds")
    calories_per_minute: Optional[float] = Field(None, ge=0)
    safety_tips: Optional[str] = None
    common_mistakes: Optional[str] = None
    alternatives: Optional[str] = None  # JSON string in database
    created_by_trainer_id: Optional[int] = None
    is_public: bool = True


class ExerciseCreate(ExerciseBase):
    """Exercise creation model."""
    created_by_trainer_id: Optional[int] = None
    is_public: bool = True


class ExerciseUpdate(BaseModel):
    """Exercise update model."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    instructions: Optional[List[str]] = None
    category: Optional[str] = None
    muscle_groups: Optional[List[str]] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    tips: Optional[List[str]] = None
    default_sets: Optional[int] = Field(None, ge=1)
    default_reps: Optional[str] = None
    default_weight: Optional[float] = Field(None, ge=0)
    default_duration: Optional[int] = Field(None, ge=0)
    rest_time: Optional[int] = Field(None, ge=0)
    calories_per_minute: Optional[float] = Field(None, ge=0)
    safety_tips: Optional[str] = None
    common_mistakes: Optional[str] = None
    alternatives: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class ExerciseResponse(ExerciseBase):
    """Exercise response model."""
    id: int
    image_url: Optional[str]
    video_url: Optional[str]
    animation_url: Optional[str]
    is_active: bool
    is_public: bool
    created_by_trainer_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @field_validator('instructions', mode='before')
    @classmethod
    def parse_instructions(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    @field_validator('muscle_groups', mode='before')
    @classmethod
    def parse_muscle_groups(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    @field_validator('tips', mode='before')
    @classmethod
    def parse_tips(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    model_config = ConfigDict(from_attributes=True)


class ExerciseSearch(BaseModel):
    """Exercise search parameters."""
    name: Optional[str] = None
    category: Optional[str] = None
    muscle_groups: Optional[List[str]] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    created_by_trainer_id: Optional[int] = None
    is_public: Optional[bool] = True


class ExerciseFilter(BaseModel):
    """Exercise filtering parameters."""
    category: Optional[str] = None
    exercise_type: Optional[str] = None
    primary_muscle_group: Optional[str] = None
    muscle_group: Optional[str] = None
    equipment_needed: Optional[str] = None
    equipment: Optional[str] = None
    difficulty_level: Optional[int] = None  # Changed to int to match API
    max_duration_minutes: Optional[int] = None
    search: Optional[str] = None
    is_public: Optional[bool] = True
    created_by_trainer_id: Optional[int] = None


class ExerciseLibrary(BaseModel):
    """Exercise library with categories."""
    categories: List[str]
    muscle_groups: List[str]
    equipment_types: List[str]
    difficulty_levels: List[str]
    total_exercises: int
