from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.schemas.user import UserResponse, UserListResponse
from app.models.user import User

# Users endpoints
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserListResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of users (admin/trainer only)."""
    # For now, let any authenticated user see the list
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserListResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)
