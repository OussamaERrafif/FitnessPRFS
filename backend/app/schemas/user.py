from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=10)
    height: Optional[float] = Field(None, gt=0, description="Height in cm")
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=6)
    role: str = Field(default="client", description="User role")


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=10)
    height: Optional[float] = Field(None, gt=0)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None


class UserResponse(UserBase):
    """User response model."""
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """User list response model."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserStats(BaseModel):
    """User statistics model."""
    total_workouts: int
    total_exercises: int
    personal_records: int
    current_programs: int
    total_sessions: int
    days_active: int
    
    model_config = ConfigDict(from_attributes=True)
