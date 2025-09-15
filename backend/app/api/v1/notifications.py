from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.notification_service import notification_service
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse,
    NotificationPreferencesCreate,
    NotificationPreferencesUpdate,
    NotificationPreferencesResponse,
    SendNotificationRequest,
    NotificationStats,
    NotificationFilter
)
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ============ NOTIFICATION TEMPLATES ============

@router.post("/templates", response_model=NotificationTemplateResponse)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new notification template (admins only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create notification templates"
        )
    
    try:
        template = notification_service.create_template(db, template_data)
        return NotificationTemplateResponse.model_validate(template)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification template"
        )


@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def get_notification_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all notification templates (admins only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view notification templates"
        )
    
    templates = notification_service.get_templates(db, skip, limit)
    return [NotificationTemplateResponse.model_validate(template) for template in templates]


@router.get("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def get_notification_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification template by ID (admins only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view notification templates"
        )
    
    template = notification_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification template not found"
        )
    
    return NotificationTemplateResponse.model_validate(template)


# ============ NOTIFICATION PREFERENCES ============

@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_my_notification_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's notification preferences."""
    preferences = notification_service.get_user_preferences(db, current_user.id)
    
    if not preferences:
        # Create default preferences if none exist
        preferences = notification_service.create_default_preferences(db, current_user.id)
    
    return NotificationPreferencesResponse.model_validate(preferences)


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_my_notification_preferences(
    preferences_data: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's notification preferences."""
    try:
        preferences = notification_service.update_user_preferences(
            db, current_user.id, preferences_data
        )
        return NotificationPreferencesResponse.model_validate(preferences)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )


@router.get("/preferences/{user_id}", response_model=NotificationPreferencesResponse)
async def get_user_notification_preferences(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's notification preferences (admins only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view other users' notification preferences"
        )
    
    preferences = notification_service.get_user_preferences(db, user_id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User notification preferences not found"
        )
    
    return NotificationPreferencesResponse.model_validate(preferences)


# ============ NOTIFICATIONS ============

@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    notification_request: SendNotificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a notification."""
    # Determine recipient(s)
    user_ids = []
    
    if notification_request.user_id:
        # Sending to specific user
        if current_user.role.value == "admin":
            user_ids = [notification_request.user_id]
        elif current_user.role.value == "trainer":
            # Trainers can only send to their clients
            from app.services.client_service import client_service
            trainer = db.query(User).filter(User.id == current_user.id).first().trainer_profile
            if trainer:
                clients = client_service.get_trainer_clients(db, trainer.id)
                client_user_ids = [client.user_id for client in clients]
                if notification_request.user_id in client_user_ids:
                    user_ids = [notification_request.user_id]
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Trainers can only send notifications to their clients"
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to send notifications"
            )
    
    elif notification_request.user_ids:
        # Sending to multiple users (admins only)
        if current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can send bulk notifications"
            )
        user_ids = notification_request.user_ids
    
    else:
        # No recipient specified
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify user_id or user_ids"
        )
    
    # Send notifications
    notifications = []
    for user_id in user_ids:
        notification_data = NotificationCreate(
            user_id=user_id,
            notification_type=notification_request.notification_type,
            category=notification_request.category,
            subject=notification_request.subject,
            title=notification_request.title,
            body=notification_request.body,
            template_id=notification_request.template_id,
            template_variables=notification_request.template_variables,
            scheduled_for=notification_request.scheduled_for
        )
        
        try:
            notification = notification_service.create_notification(db, notification_data)
            notifications.append(notification)
        except Exception as e:
            # Log error but continue with other notifications
            pass
    
    if not notifications:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send any notifications"
        )
    
    # Return the first notification (or you could return all)
    return NotificationResponse.model_validate(notifications[0])


@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's notifications."""
    notifications = notification_service.get_user_notifications(
        db, current_user.id, skip, limit, category, unread_only
    )
    return [NotificationResponse.model_validate(notification) for notification in notifications]


@router.get("/all", response_model=List[NotificationResponse])
async def get_all_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all notifications (admins only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all notifications"
        )
    
    # This would need a more sophisticated filtering method in the service
    # For now, just get user notifications if user_id is specified
    if user_id:
        notifications = notification_service.get_user_notifications(
            db, user_id, skip, limit, category
        )
    else:
        # Return empty for now - would need to implement get_all_notifications in service
        notifications = []
    
    return [NotificationResponse.model_validate(notification) for notification in notifications]


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    success = notification_service.mark_notification_read(db, notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or already read"
        )
    
    return {"message": "Notification marked as read"}


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics."""
    # Users can only see their own stats unless they're admin
    if user_id and current_user.role.value != "admin":
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own notification statistics"
            )
    
    # If no user_id specified, use current user (unless admin)
    if not user_id:
        user_id = current_user.id if current_user.role.value != "admin" else None
    
    stats = notification_service.get_notification_stats(db, user_id)
    return NotificationStats(**stats)
