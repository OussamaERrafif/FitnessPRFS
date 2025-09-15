from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class NotificationTemplateBase(BaseModel):
    """Base notification template model."""
    name: str = Field(..., max_length=255, description="Template name")
    category: str = Field(..., description="Notification category")
    notification_type: str = Field(..., description="Notification type")
    subject: Optional[str] = Field(None, max_length=500, description="Email subject")
    title: Optional[str] = Field(None, max_length=255, description="Push notification title")
    body: str = Field(..., description="Notification body")
    variables: Optional[List[str]] = Field(None, description="Template variables")
    is_active: bool = Field(True, description="Whether template is active")


class NotificationTemplateCreate(NotificationTemplateBase):
    """Notification template creation model."""
    pass


class NotificationTemplateUpdate(BaseModel):
    """Notification template update model."""
    name: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = None
    notification_type: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=500)
    title: Optional[str] = Field(None, max_length=255)
    body: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Notification template response model."""
    id: int
    is_system_template: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class NotificationBase(BaseModel):
    """Base notification model."""
    user_id: int = Field(..., description="Recipient user ID")
    notification_type: str = Field(..., description="Notification type")
    category: str = Field(..., description="Notification category")
    subject: Optional[str] = Field(None, max_length=500)
    title: Optional[str] = Field(None, max_length=255)
    body: str = Field(..., description="Notification body")
    recipient_email: Optional[EmailStr] = Field(None, description="Recipient email")
    recipient_phone: Optional[str] = Field(None, max_length=20, description="Recipient phone")
    scheduled_for: Optional[datetime] = Field(None, description="When to send notification")
    expires_at: Optional[datetime] = Field(None, description="When notification expires")


class NotificationCreate(NotificationBase):
    """Notification creation model."""
    template_id: Optional[int] = Field(None, description="Template ID to use")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="Variables for template")


class NotificationResponse(NotificationBase):
    """Notification response model."""
    id: int
    status: str
    template_id: Optional[int]
    template_variables: Optional[Dict[str, Any]]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    failed_at: Optional[datetime]
    failure_reason: Optional[str]
    external_id: Optional[str]
    provider: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class NotificationPreferencesBase(BaseModel):
    """Base notification preferences model."""
    email_enabled: bool = Field(True, description="Enable email notifications")
    email_session_reminders: bool = Field(True, description="Email session reminders")
    email_program_updates: bool = Field(True, description="Email program updates")
    email_marketing: bool = Field(False, description="Email marketing notifications")
    
    sms_enabled: bool = Field(False, description="Enable SMS notifications")
    sms_session_reminders: bool = Field(False, description="SMS session reminders")
    sms_urgent_only: bool = Field(True, description="SMS for urgent notifications only")
    
    push_enabled: bool = Field(True, description="Enable push notifications")
    push_session_reminders: bool = Field(True, description="Push session reminders")
    push_progress_updates: bool = Field(True, description="Push progress updates")
    
    in_app_enabled: bool = Field(True, description="Enable in-app notifications")
    
    reminder_hours_before: int = Field(24, ge=1, le=168, description="Hours before session to remind")
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: Optional[str] = Field(None, max_length=50)


class NotificationPreferencesCreate(NotificationPreferencesBase):
    """Notification preferences creation model."""
    user_id: int = Field(..., description="User ID")


class NotificationPreferencesUpdate(BaseModel):
    """Notification preferences update model."""
    email_enabled: Optional[bool] = None
    email_session_reminders: Optional[bool] = None
    email_program_updates: Optional[bool] = None
    email_marketing: Optional[bool] = None
    
    sms_enabled: Optional[bool] = None
    sms_session_reminders: Optional[bool] = None
    sms_urgent_only: Optional[bool] = None
    
    push_enabled: Optional[bool] = None
    push_session_reminders: Optional[bool] = None
    push_progress_updates: Optional[bool] = None
    
    in_app_enabled: Optional[bool] = None
    
    reminder_hours_before: Optional[int] = Field(None, ge=1, le=168)
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: Optional[str] = Field(None, max_length=50)


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Notification preferences response model."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class SendNotificationRequest(BaseModel):
    """Request model for sending notifications."""
    user_id: Optional[int] = Field(None, description="Specific user ID (admin only)")
    user_ids: Optional[List[int]] = Field(None, description="Multiple user IDs (admin only)")
    notification_type: str = Field(..., description="Notification type")
    category: str = Field(..., description="Notification category")
    subject: Optional[str] = Field(None, max_length=500)
    title: Optional[str] = Field(None, max_length=255)
    body: Optional[str] = Field(None, description="Notification body")
    template_id: Optional[int] = Field(None, description="Template ID to use")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="Variables for template")
    scheduled_for: Optional[datetime] = Field(None, description="When to send notification")


class NotificationStats(BaseModel):
    """Notification statistics model."""
    total_notifications: int
    sent_notifications: int
    delivered_notifications: int
    failed_notifications: int
    read_notifications: int
    pending_notifications: int


class NotificationFilter(BaseModel):
    """Notification filtering model."""
    user_id: Optional[int] = None
    notification_type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
