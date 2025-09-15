from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import TokenData
from app.config.logging_config import log_security_event, get_logger
from app.utils.logging_utils import get_service_logger, log_service_method
from app.utils.api_logging import api_logger, log_security_event as log_api_security_event

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Service logger
service_logger = get_service_logger("auth")


class AuthService:
    """Authentication service for handling user auth operations."""
    
    @staticmethod
    @log_service_method("auth", "verify_password")
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        result = pwd_context.verify(plain_password, hashed_password)
        
        if not result:
            log_security_event("password_verification_failed", {
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return result
    
    @staticmethod
    @log_service_method("auth", "hash_password")
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        service_logger.debug("Generating password hash")
        return pwd_context.hash(password)
    
    @staticmethod
    @log_service_method("auth", "create_access_token")
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        # Ensure payload is a plain dict (handle pydantic models)
        if hasattr(to_encode, "model_dump"):
            to_encode = to_encode.model_dump()
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        
        # Log token creation (without sensitive data)
        log_security_event("access_token_created", {
            "user_id": data.get("sub"),
            "expires_at": expire.isoformat()
        }, user_id=data.get("sub"))
        
        return encoded_jwt
    
    @staticmethod
    @log_service_method("auth", "create_refresh_token")
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        if hasattr(to_encode, "model_dump"):
            to_encode = to_encode.model_dump()
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
        """Verify and decode JWT token. Returns payload dict or None if invalid/expired."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None
    
    @staticmethod
    @log_service_method("auth", "authenticate_user")
    def authenticate_user(db: Session, email: str, password: str, request_id: str = None, client_ip: str = None) -> Optional[User]:
        """Authenticate user with email and password."""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Log failed authentication - user not found
            api_logger.log_authentication_attempt(
                username=email,
                success=False,
                request_id=request_id or "unknown",
                client_ip=client_ip or "unknown",
                failure_reason="user_not_found"
            )
            return None
            
        if not AuthService.verify_password(password, user.hashed_password):
            # Log failed authentication - wrong password
            api_logger.log_authentication_attempt(
                username=email,
                success=False,
                request_id=request_id or "unknown",
                client_ip=client_ip or "unknown",
                failure_reason="invalid_password"
            )
            return None
            
        # Log successful authentication
        api_logger.log_authentication_attempt(
            username=email,
            success=True,
            request_id=request_id or "unknown",
            client_ip=client_ip or "unknown"
        )
        
        return user
    
    @staticmethod
    def create_user_tokens(user: User) -> dict:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from JWT token."""
        token_data = AuthService.verify_token(token)
        
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        token_data = AuthService.verify_token(refresh_token, "refresh")
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = token_data.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        return AuthService.create_user_tokens(user)
    
    @staticmethod
    def register_user(db: Session, email: str, username: Optional[str], password: str, 
                     full_name: Optional[str] = None, role: str = "client") -> User:
        """Register a new user."""
        # Check if user already exists
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # If username is provided, check if it's taken
        if username and db.query(User).filter(User.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Generate username from email if not provided
        if not username:
            username = email.split('@')[0]
            # Ensure uniqueness by adding number if needed
            original_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{original_username}{counter}"
                counter += 1
        
        # Create new user
        hashed_password = AuthService.get_password_hash(password)
        
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole(role)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    @log_service_method("auth", "get_current_user")
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from JWT token."""
        token_data = AuthService.verify_token(token)
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user

    # Helper methods used by tests
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()


# Global auth service instance
auth_service = AuthService()
