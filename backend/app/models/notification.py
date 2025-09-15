from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class NotificationType(PyEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(PyEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationCategory(PyEnum):
    WELCOME = "welcome"
    PIN_GENERATED = "pin_generated"
    SESSION_REMINDER = "session_reminder"
    SESSION_CANCELLED = "session_cancelled"
    SESSION_RESCHEDULED = "session_rescheduled"
    PROGRAM_ASSIGNED = "program_assigned"
    MEAL_PLAN_ASSIGNED = "meal_plan_assigned"
    PROGRESS_UPDATE = "progress_update"
    PAYMENT_REMINDER = "payment_reminder"
    SYSTEM_ALERT = "system_alert"
    MARKETING = "marketing"


class NotificationTemplate(Base):
    """Notification template model for reusable notification content."""
    
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template identification
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(50), nullable=False)  # NotificationCategory enum as string
    notification_type = Column(String(50), nullable=False)  # NotificationType enum as string
    
    # Template content
    subject = Column(String(500), nullable=True)  # For email notifications
    title = Column(String(255), nullable=True)  # For push/in-app notifications
    body = Column(Text, nullable=False)
    
    # Template variables (JSON list of expected variables)
    variables = Column(JSON, nullable=True)
    
    # Template settings
    is_active = Column(Boolean, default=True)
    is_system_template = Column(Boolean, default=False)  # Cannot be deleted if True
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"


class Notification(Base):
    """Notification model for tracking sent notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    
    # Notification details
    notification_type = Column(String(50), nullable=False)  # NotificationType enum as string
    category = Column(String(50), nullable=False)  # NotificationCategory enum as string
    status = Column(String(50), default=NotificationStatus.PENDING.value)  # NotificationStatus enum as string
    
    # Content
    subject = Column(String(500), nullable=True)
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    
    # Metadata
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    template_variables = Column(JSON, nullable=True)  # Variables used to populate template
    
    # Delivery tracking
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # External service tracking
    external_id = Column(String(255), nullable=True)  # ID from email/SMS service
    provider = Column(String(100), nullable=True)  # Email/SMS provider used
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)  # For delayed notifications
    expires_at = Column(DateTime, nullable=True)  # When notification expires
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    template = relationship("NotificationTemplate")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}', status='{self.status}')>"


class NotificationPreference(Base):
    """User notification preferences model."""
    
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Email preferences
    email_enabled = Column(Boolean, default=True)
    email_session_reminders = Column(Boolean, default=True)
    email_program_updates = Column(Boolean, default=True)
    email_marketing = Column(Boolean, default=False)
    
    # SMS preferences
    sms_enabled = Column(Boolean, default=False)
    sms_session_reminders = Column(Boolean, default=False)
    sms_urgent_only = Column(Boolean, default=True)
    
    # Push notification preferences
    push_enabled = Column(Boolean, default=True)
    push_session_reminders = Column(Boolean, default=True)
    push_progress_updates = Column(Boolean, default=True)
    
    # In-app notification preferences
    in_app_enabled = Column(Boolean, default=True)
    
    # Timing preferences
    reminder_hours_before = Column(Integer, default=24)  # Hours before session to send reminder
    quiet_hours_start = Column(String(5), nullable=True)  # e.g., "22:00"
    quiet_hours_end = Column(String(5), nullable=True)    # e.g., "08:00"
    timezone = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")
    
    def __repr__(self):
        return f"<NotificationPreference(id={self.id}, user_id={self.user_id})>"
