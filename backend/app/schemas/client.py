from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ClientBase(BaseModel):
    """Base client model."""
    age: Optional[int] = Field(None, ge=13, le=120, description="Age in years")
    height: Optional[float] = Field(None, gt=0, le=300, description="Height in cm")
    fitness_level: Optional[str] = Field(None, description="Fitness level (beginner, intermediate, advanced)")
    current_weight: Optional[float] = Field(None, gt=0, description="Current weight in kg")
    target_weight: Optional[float] = Field(None, gt=0, description="Target weight in kg")
    activity_level: Optional[str] = Field(None, description="Activity level")
    fitness_goals: Optional[List[str]] = Field(None, description="List of fitness goals")
    medical_conditions: Optional[List[str]] = Field(None, description="Medical conditions")
    injuries: Optional[List[str]] = Field(None, description="Past or current injuries")
    medications: Optional[List[str]] = Field(None, description="Current medications")
    preferred_workout_days: Optional[List[str]] = Field(None, description="Preferred workout days")
    preferred_workout_time: Optional[str] = Field(None, description="Preferred workout time")
    workout_experience: Optional[str] = Field(None, description="Workout experience level")
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)


class ClientCreate(ClientBase):
    """Client creation model."""
    pass  # No user_id required - it will be set from authenticated user


class ClientCreateWithUserId(ClientBase):
    """Client creation model with explicit user_id (for admin use)."""
    user_id: int = Field(..., description="Associated user ID")


class ClientCreateInternal(ClientBase):
    """Internal client creation model with user_id."""
    user_id: int = Field(..., description="Associated user ID")


class ClientUpdate(ClientBase):
    """Client update model."""
    pass


class ClientResponse(ClientBase):
    """Client response model."""
    id: int
    user_id: int
    assigned_trainer_id: Optional[int]
    membership_type: Optional[str]
    membership_start_date: Optional[datetime]
    membership_end_date: Optional[datetime]
    is_membership_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Client PIN for self-service access
    pin_code: Optional[str] = Field(None, description="Client PIN for self-service access")
    
    model_config = ConfigDict(from_attributes=True)


class ClientPINAccess(BaseModel):
    """Client PIN access model."""
    pin_code: str = Field(..., min_length=4, max_length=8, description="Client PIN code")


class ClientPINLogin(BaseModel):
    """Client PIN login response."""
    client_id: int
    user_id: int
    full_name: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ClientProfileUpdate(BaseModel):
    """Client profile update via PIN access."""
    current_weight: Optional[float] = Field(None, gt=0)
    target_weight: Optional[float] = Field(None, gt=0)
    fitness_goals: Optional[List[str]] = None
    notes: Optional[str] = Field(None, description="Client notes or feedback")


class ClientStats(BaseModel):
    """Client statistics model."""
    total_sessions: int
    completed_sessions: int
    completed_workouts: int
    active_programs: int
    total_workouts_logged: int
    current_streak_days: int
    total_weight_change: Optional[float]
    weight_progress: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)
