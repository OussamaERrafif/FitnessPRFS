from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.auth_service import auth_service
from app.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    AuthResponse, 
    RefreshTokenRequest,
    PasswordChangeRequest,
    UserProfile,
    UpdateProfile
)
from app.models.user import User

# Auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    try:
        # Register user
        user = auth_service.register_user(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        
        # Create tokens
        tokens = auth_service.create_user_tokens(user)
        
        return AuthResponse(
            user_id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value,
            is_verified=user.is_verified,
            **tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens."""
    user = auth_service.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    tokens = auth_service.create_user_tokens(user)
    
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        is_verified=user.is_verified,
        **tokens
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        tokens = auth_service.refresh_access_token(db, request.refresh_token)
        return tokens
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile."""
    return UserProfile.model_validate(current_user)


@router.put("/me", response_model=UserProfile)
async def update_profile(
    request: UpdateProfile,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    # Update user fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    from datetime import datetime
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfile.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    # Verify current password
    if not auth_service.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = auth_service.get_password_hash(request.new_password)
    from datetime import datetime
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password changed successfully"}
