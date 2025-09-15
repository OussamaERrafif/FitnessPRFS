from datetime import datetime, time, date
from typing import List, Optional, Dict, Any
import json
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TrainerBase(BaseModel):
    """Base trainer model."""
    certification: Optional[str] = Field(None, max_length=255)
    specializations: Optional[List[str]] = Field(None, description="List of specializations")
    years_of_experience: Optional[int] = Field(None, ge=0)
    experience_years: Optional[int] = Field(None, ge=0, description="Years of experience (alias)")
    education: Optional[str] = Field(None, description="Educational background")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate in currency")
    bio: Optional[str] = Field(None, description="Professional bio")
    services_offered: Optional[List[str]] = Field(None, description="Services offered")
    available_days: Optional[List[str]] = Field(None, description="Available days of week")
    available_hours: Optional[str] = Field(None, description="Available hours range")
    timezone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255, description="Combined location")
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    offers_online_training: bool = False
    offers_in_person_training: bool = True


class TrainerCreate(TrainerBase):
    """Trainer creation model."""
    user_id: Optional[int] = Field(None, description="Associated user ID (set automatically)")


class TrainerUpdate(TrainerBase):
    """Trainer update model."""
    is_available: Optional[bool] = None


class TrainerResponse(TrainerBase):
    """Trainer response model."""
    id: int
    user_id: int
    is_verified: bool
    is_available: bool
    average_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('specializations', mode='before')
    @classmethod
    def parse_specializations(cls, v):
        """Convert JSON string to list for specializations."""
        if isinstance(v, str):
            try:
                # Handle both JSON string and Python string representation
                if v.startswith('[') and v.endswith(']'):
                    return eval(v)  # Safe for list literals
                return json.loads(v)
            except (json.JSONDecodeError, SyntaxError):
                return []
        return v if v is not None else []
    
    @field_validator('services_offered', mode='before')
    @classmethod
    def parse_services_offered(cls, v):
        """Convert JSON string to list for services_offered."""
        if isinstance(v, str):
            try:
                if v.startswith('[') and v.endswith(']'):
                    return eval(v)
                return json.loads(v)
            except (json.JSONDecodeError, SyntaxError):
                return []
        return v if v is not None else []
    
    @field_validator('available_days', mode='before')
    @classmethod
    def parse_available_days(cls, v):
        """Convert JSON string to list for available_days."""
        if isinstance(v, str):
            try:
                if v.startswith('[') and v.endswith(']'):
                    return eval(v)
                return json.loads(v)
            except (json.JSONDecodeError, SyntaxError):
                return []
        return v if v is not None else []


class TrainerPublicProfile(BaseModel):
    """Public trainer profile for client browsing."""
    id: int
    full_name: str
    bio: Optional[str]
    specializations: Optional[List[str]]
    years_of_experience: Optional[int]
    hourly_rate: Optional[float]
    average_rating: float
    total_reviews: int
    city: Optional[str]
    state: Optional[str]
    offers_online_training: bool
    offers_in_person_training: bool
    is_available: bool
    
    model_config = ConfigDict(from_attributes=True)


class TrainerAvailability(BaseModel):
    """Trainer availability model."""
    trainer_id: int
    available_days: List[str]
    available_hours: str
    timezone: str
    is_available: bool


class TrainerStats(BaseModel):
    """Trainer statistics model."""
    total_clients: int
    active_clients: int
    sessions_this_month: int
    revenue_this_month: float
    average_rating: float
    total_sessions: int
    certification_count: int
    
    model_config = ConfigDict(from_attributes=True)


# Trainer Certification Schemas
class TrainerCertificationBase(BaseModel):
    """Base certification model."""
    name: str = Field(..., max_length=200)
    issuing_organization: Optional[str] = Field(None, max_length=200)
    certification_number: Optional[str] = Field(None, max_length=100)
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    is_current: bool = True


class TrainerCertificationCreate(TrainerCertificationBase):
    """Certification creation model."""
    pass


class TrainerCertificationUpdate(TrainerCertificationBase):
    """Certification update model."""
    name: Optional[str] = Field(None, max_length=200)
    is_current: Optional[bool] = None


class TrainerCertificationResponse(TrainerCertificationBase):
    """Certification response model."""
    id: int
    trainer_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# Trainer Availability Schemas
class TrainerAvailabilityBase(BaseModel):
    """Base availability model."""
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    is_available: bool = True


class TrainerAvailabilityCreate(TrainerAvailabilityBase):
    """Availability creation model."""
    pass


class TrainerAvailabilityUpdate(TrainerAvailabilityBase):
    """Availability update model."""
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None


class TrainerAvailabilityResponse(TrainerAvailabilityBase):
    """Availability response model."""
    id: int
    trainer_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# Dashboard Schema
class TrainerDashboard(BaseModel):
    """Trainer dashboard data."""
    trainer_info: TrainerResponse
    stats: TrainerStats
    today_sessions: List[Dict[str, Any]]
    upcoming_sessions: List[Dict[str, Any]]
    recent_clients: List[Dict[str, Any]]
    notifications: List[str]
    
    model_config = ConfigDict(from_attributes=True)
