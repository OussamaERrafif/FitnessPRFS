from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data for JWT payload."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class LoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")


class RegisterRequest(BaseModel):
    """User registration request model."""
    email: EmailStr = Field(..., description="User's email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="User's password")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    role: str = Field(default="client", description="User role: client, trainer, or admin")


class PasswordChangeRequest(BaseModel):
    """Password change request model."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=6, description="New password")


class EmailVerificationRequest(BaseModel):
    """Email verification request model."""
    email: EmailStr = Field(..., description="Email to verify")


class EmailVerificationConfirm(BaseModel):
    """Email verification confirmation model."""
    token: str = Field(..., description="Verification token")


class AuthResponse(BaseModel):
    """Authentication response model."""
    user_id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_verified: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    """User profile response model."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    phone: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    height: Optional[float]
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class UpdateProfile(BaseModel):
    """Update user profile request model."""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=10)
    height: Optional[float] = Field(None, gt=0, description="Height in cm")
    bio: Optional[str] = None
