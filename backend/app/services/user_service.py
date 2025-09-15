from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import AuthService


class UserService:
    """Service for user management operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user_dict = user_data.model_dump()
        password = user_dict.pop('password')
        user_dict['hashed_password'] = AuthService.get_password_hash(password)
        
        db_user = User(**user_dict)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def search_users_by_name(db: Session, search_term: str) -> List[User]:
        """Search users by name (full name)."""
        return db.query(User).filter(
            User.full_name.ilike(f"%{search_term}%")
        ).all()
    
    @staticmethod
    def get_users_by_role(db: Session, role: UserRole) -> List[User]:
        """Get users by role."""
        return db.query(User).filter(User.role == role).all()
    
    @staticmethod
    def get_user_count(db: Session) -> int:
        """Get total user count."""
        return db.query(User).count()
    
    @staticmethod
    def get_active_users(db: Session) -> List[User]:
        """Get active users only."""
        return db.query(User).filter(User.is_active == True).all()
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[User]:
        """Deactivate a user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.is_active = False
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> Optional[User]:
        """Activate a user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def verify_email(db: Session, user_id: int) -> Optional[User]:
        """Verify user's email."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.is_verified = True
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> Optional[User]:
        """Change user's password."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not AuthService.verify_password(current_password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        db_user.hashed_password = AuthService.get_password_hash(new_password)
        db.commit()
        db.refresh(db_user)
        return db_user