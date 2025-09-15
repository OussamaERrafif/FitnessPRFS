from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class AttachmentType(PyEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    OTHER = "other"


class AttachmentCategory(PyEnum):
    EXERCISE_MEDIA = "exercise_media"
    RECIPE_MEDIA = "recipe_media"
    PROFILE_PICTURE = "profile_picture"
    SESSION_DOCUMENT = "session_document"
    PROGRAM_MATERIAL = "program_material"
    PROGRESS_PHOTO = "progress_photo"
    MEAL_PHOTO = "meal_photo"
    CERTIFICATE = "certificate"
    OTHER = "other"


class Attachment(Base):
    """Attachment model for file uploads."""
    
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=True)  # Public URL if available
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    
    # Classification
    attachment_type = Column(Enum(AttachmentType), nullable=False)
    category = Column(Enum(AttachmentCategory), nullable=False)
    
    # Ownership and associations
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Related entities (optional - can be attached to various entities)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("session_bookings.id"), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    progress_log_id = Column(Integer, ForeignKey("progress_logs.id"), nullable=True)
    
    # Metadata
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    alt_text = Column(String(255), nullable=True)  # For accessibility
    
    # Image/Video specific metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # For video/audio files
    
    # Processing status
    is_processed = Column(Boolean, default=True)
    processing_status = Column(String(50), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    
    # Security and access
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploaded_by = relationship("User", backref="uploaded_attachments")
    exercise = relationship("Exercise", backref="attachments")
    recipe = relationship("Recipe", backref="attachments")
    session = relationship("SessionBooking", backref="attachments")
    program = relationship("Program", backref="attachments")
    progress_log = relationship("ProgressLog", backref="attachments")
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}', type='{self.attachment_type}')>"
