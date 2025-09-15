from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class UserRole(PyEnum):
    CLIENT = "client"
    TRAINER = "trainer"
    ADMIN = "admin"


class User(Base):
    """User model for authentication and basic info."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Profile information
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)
    height = Column(Float, nullable=True)  # in cm
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Profile picture
    avatar_url = Column(String(500), nullable=True)
    
    # Bio/description
    bio = Column(Text, nullable=True)
    
    # Relationships
    client_profile = relationship("Client", back_populates="user", uselist=False)
    trainer_profile = relationship("Trainer", back_populates="user", uselist=False)
    progress_logs = relationship("ProgressLog", back_populates="user")
    session_bookings = relationship("SessionBooking", back_populates="client")
    notifications = relationship("Notification", back_populates="user")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
