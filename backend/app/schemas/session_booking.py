from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SessionBookingBase(BaseModel):
    """Base session booking model."""
    session_type: str = Field(..., description="Type of session")
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    scheduled_start: datetime = Field(..., description="Scheduled start time")
    scheduled_end: datetime = Field(..., description="Scheduled end time")
    duration_minutes: int = Field(60, ge=15, le=480, description="Session duration in minutes")
    location: Optional[str] = None
    room_number: Optional[str] = None
    online_meeting_url: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    planned_activities: Optional[List[str]] = Field(None, description="Planned activities")


class SessionBookingCreate(SessionBookingBase):
    """Session booking creation model."""
    trainer_id: int = Field(..., description="Trainer ID")
    client_id: Optional[int] = Field(None, description="Client ID (if booking for specific client)")


class SessionBookingUpdate(BaseModel):
    """Session booking update model."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    location: Optional[str] = None
    room_number: Optional[str] = None
    online_meeting_url: Optional[str] = None
    online_meeting_id: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None
    planned_activities: Optional[List[str]] = None
    actual_activities: Optional[List[str]] = None
    trainer_notes_before: Optional[str] = None
    trainer_notes_after: Optional[str] = None
    client_notes: Optional[str] = None
    goals_achieved: Optional[List[str]] = None
    homework_assigned: Optional[str] = None
    next_session_recommendations: Optional[str] = None


class SessionBookingResponse(SessionBookingBase):
    """Session booking response model."""
    id: int
    client_id: int
    trainer_id: int
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    status: str
    online_meeting_id: Optional[str]
    is_paid: bool
    payment_method: Optional[str]
    actual_activities: Optional[List[str]]
    trainer_notes_before: Optional[str]
    trainer_notes_after: Optional[str]
    client_notes: Optional[str]
    goals_achieved: Optional[List[str]]
    homework_assigned: Optional[str]
    next_session_recommendations: Optional[str]
    client_rating: Optional[int]
    trainer_rating: Optional[int]
    client_feedback: Optional[str]
    trainer_feedback: Optional[str]
    client_attended: Optional[bool]
    trainer_attended: Optional[bool]
    original_session_id: Optional[int]
    reschedule_reason: Optional[str]
    rescheduled_by: Optional[str]
    reminder_sent: bool
    confirmation_sent: bool
    created_at: datetime
    updated_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    
    # Related data
    client_name: Optional[str] = None
    trainer_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SessionReschedule(BaseModel):
    """Session reschedule model."""
    session_id: int
    new_start_time: datetime
    new_end_time: datetime
    reschedule_reason: str
    rescheduled_by: str  # "client" or "trainer"


class SessionFeedback(BaseModel):
    """Session feedback model."""
    session_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback: Optional[str] = None
    goals_achieved: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None


class SessionAttendance(BaseModel):
    """Session attendance model."""
    session_id: int
    client_attended: bool
    trainer_attended: bool
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    no_show_reason: Optional[str] = None


class AvailableTimeSlot(BaseModel):
    """Available time slot model."""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    trainer_id: int
    trainer_name: str
    hourly_rate: Optional[float]
    location: Optional[str]
    session_types: List[str]


class TrainerSchedule(BaseModel):
    """Trainer schedule model."""
    trainer_id: int
    trainer_name: str
    date: datetime
    available_slots: List[AvailableTimeSlot]
    booked_sessions: List[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)


class SessionCalendar(BaseModel):
    """Session calendar view."""
    date: datetime
    sessions: List[SessionBookingResponse]
    available_slots: List[AvailableTimeSlot]
    
    model_config = ConfigDict(from_attributes=True)


class SessionStats(BaseModel):
    """Session statistics."""
    total_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    no_show_sessions: int
    average_rating: Optional[float]
    total_revenue: Optional[float]
    upcoming_sessions: int
    
    model_config = ConfigDict(from_attributes=True)


class SessionBookingFilter(BaseModel):
    """Session booking filter model."""
    client_id: Optional[int] = None
    trainer_id: Optional[int] = None
    status: Optional[str] = None
    session_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TimeSlot(BaseModel):
    """Time slot model."""
    start_time: datetime
    end_time: datetime
    is_available: bool
    trainer_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class SessionSummary(BaseModel):
    """Session summary model."""
    session_id: int
    client_name: str
    trainer_name: str
    scheduled_date: datetime
    duration_minutes: int
    status: str
    session_type: str
    
    model_config = ConfigDict(from_attributes=True)
