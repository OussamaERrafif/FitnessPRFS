import asyncio
import smtplib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.notification import (
    Notification, 
    NotificationTemplate, 
    NotificationPreference,
    NotificationType,
    NotificationStatus,
    NotificationCategory
)
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationTemplateCreate,
    NotificationPreferencesCreate,
    NotificationPreferencesUpdate,
    SendNotificationRequest
)

# Configure logging
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling notifications."""
    
    def __init__(self):
        # Email configuration (you can move these to environment variables)
        self.smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
        self.smtp_port = 587
        self.smtp_username = ""  # Configure in environment
        self.smtp_password = ""  # Configure in environment
        self.from_email = "noreply@fitnesspr.com"
        
        # SMS configuration (placeholder for future implementation)
        self.sms_api_key = ""  # Configure for SMS service like Twilio
        self.sms_from_number = ""
    
    # ============ NOTIFICATION TEMPLATES ============
    
    def create_template(self, db: Session, template_data: NotificationTemplateCreate) -> NotificationTemplate:
        """Create a new notification template."""
        # Check if template with same name exists
        existing = db.query(NotificationTemplate).filter(
            NotificationTemplate.name == template_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template with this name already exists"
            )
        
        template = NotificationTemplate(**template_data.model_dump())
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return template
    
    def get_template_by_id(self, db: Session, template_id: int) -> Optional[NotificationTemplate]:
        """Get notification template by ID."""
        return db.query(NotificationTemplate).filter(
            NotificationTemplate.id == template_id
        ).first()
    
    def get_template_by_name(self, db: Session, name: str) -> Optional[NotificationTemplate]:
        """Get notification template by name."""
        return db.query(NotificationTemplate).filter(
            NotificationTemplate.name == name
        ).first()
    
    def get_templates(self, db: Session, skip: int = 0, limit: int = 50) -> List[NotificationTemplate]:
        """Get all notification templates."""
        return db.query(NotificationTemplate).filter(
            NotificationTemplate.is_active == True
        ).offset(skip).limit(limit).all()
    
    # ============ NOTIFICATION PREFERENCES ============
    
    def create_default_preferences(self, db: Session, user_id: int) -> NotificationPreference:
        """Create default notification preferences for a user."""
        # Check if preferences already exist
        existing = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if existing:
            return existing
        
        preferences = NotificationPreference(user_id=user_id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
        
        return preferences
    
    def get_user_preferences(self, db: Session, user_id: int) -> Optional[NotificationPreference]:
        """Get user notification preferences."""
        return db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
    
    def update_user_preferences(
        self, 
        db: Session, 
        user_id: int, 
        preferences_data: NotificationPreferencesUpdate
    ) -> Optional[NotificationPreference]:
        """Update user notification preferences."""
        preferences = self.get_user_preferences(db, user_id)
        if not preferences:
            # Create default preferences if none exist
            preferences = self.create_default_preferences(db, user_id)
        
        update_dict = preferences_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(preferences, field, value)
        
        preferences.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(preferences)
        
        return preferences
    
    # ============ NOTIFICATION CREATION ============
    
    def create_notification(self, db: Session, notification_data: NotificationCreate) -> Notification:
        """Create a new notification."""
        # Get user info
        user = db.query(User).filter(User.id == notification_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # If using template, populate content
        if notification_data.template_id:
            template = self.get_template_by_id(db, notification_data.template_id)
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
            
            # Populate template variables
            body = template.body
            subject = template.subject
            title = template.title
            
            if notification_data.template_variables:
                for var, value in notification_data.template_variables.items():
                    placeholder = f"{{{var}}}"
                    if body:
                        body = body.replace(placeholder, str(value))
                    if subject:
                        subject = subject.replace(placeholder, str(value))
                    if title:
                        title = title.replace(placeholder, str(value))
        else:
            body = notification_data.body
            subject = notification_data.subject
            title = notification_data.title
        
        # Set recipient info
        recipient_email = notification_data.recipient_email or user.email
        # For SMS, you'd get phone from user profile
        
        notification = Notification(
            user_id=notification_data.user_id,
            notification_type=notification_data.notification_type,
            category=notification_data.category,
            subject=subject,
            title=title,
            body=body,
            recipient_email=recipient_email,
            recipient_phone=notification_data.recipient_phone,
            template_id=notification_data.template_id,
            template_variables=notification_data.template_variables,
            scheduled_for=notification_data.scheduled_for,
            expires_at=notification_data.expires_at
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Send immediately if not scheduled
        if not notification_data.scheduled_for:
            asyncio.create_task(self._send_notification(db, notification))
        
        return notification
    
    # ============ NOTIFICATION SENDING ============
    
    async def _send_notification(self, db: Session, notification: Notification) -> bool:
        """Send a notification based on its type."""
        try:
            if notification.notification_type == NotificationType.EMAIL.value:
                return await self._send_email(notification)
            elif notification.notification_type == NotificationType.SMS.value:
                return await self._send_sms(notification)
            elif notification.notification_type == NotificationType.PUSH.value:
                return await self._send_push(notification)
            elif notification.notification_type == NotificationType.IN_APP.value:
                # In-app notifications are just stored in database
                notification.status = NotificationStatus.SENT.value
                notification.sent_at = datetime.utcnow()
                notification.delivered_at = datetime.utcnow()
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {str(e)}")
            notification.status = NotificationStatus.FAILED.value
            notification.failed_at = datetime.utcnow()
            notification.failure_reason = str(e)
            db.commit()
            return False
    
    async def _send_email(self, notification: Notification) -> bool:
        """Send email notification."""
        try:
            # Skip if no SMTP configuration
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP not configured, skipping email send")
                notification.status = NotificationStatus.FAILED.value
                notification.failed_at = datetime.utcnow()
                notification.failure_reason = "SMTP not configured"
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = notification.recipient_email
            msg['Subject'] = notification.subject or "FitnessPR Notification"
            
            msg.attach(MIMEText(notification.body, 'html' if '<' in notification.body else 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, notification.recipient_email, text)
            server.quit()
            
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.utcnow()
            notification.provider = "SMTP"
            
            logger.info(f"Email sent successfully to {notification.recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise e
    
    async def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification (placeholder implementation)."""
        # This would integrate with SMS service like Twilio
        logger.info(f"SMS sending not implemented yet. Would send to: {notification.recipient_phone}")
        
        # Mock successful send for now
        notification.status = NotificationStatus.SENT.value
        notification.sent_at = datetime.utcnow()
        notification.provider = "Mock SMS"
        
        return True
    
    async def _send_push(self, notification: Notification) -> bool:
        """Send push notification (placeholder implementation)."""
        # This would integrate with push notification service
        logger.info(f"Push notification sending not implemented yet. Title: {notification.title}")
        
        # Mock successful send for now
        notification.status = NotificationStatus.SENT.value
        notification.sent_at = datetime.utcnow()
        notification.provider = "Mock Push"
        
        return True
    
    # ============ AUTOMATED NOTIFICATIONS ============
    
    def send_pin_generated_notification(self, db: Session, user_id: int, pin_code: str) -> Notification:
        """Send PIN generated notification to client."""
        template = self.get_template_by_name(db, "client_pin_generated")
        
        if template:
            notification_data = NotificationCreate(
                user_id=user_id,
                notification_type=NotificationType.EMAIL.value,
                category=NotificationCategory.PIN_GENERATED.value,
                template_id=template.id,
                template_variables={"pin_code": pin_code}
            )
        else:
            # Fallback if no template
            notification_data = NotificationCreate(
                user_id=user_id,
                notification_type=NotificationType.EMAIL.value,
                category=NotificationCategory.PIN_GENERATED.value,
                subject="Your FitnessPR Access PIN",
                body=f"Your access PIN is: {pin_code}. Use this PIN to access your fitness dashboard."
            )
        
        return self.create_notification(db, notification_data)
    
    def send_session_reminder(self, db: Session, user_id: int, session_details: Dict[str, Any]) -> Notification:
        """Send session reminder notification."""
        template = self.get_template_by_name(db, "session_reminder")
        
        if template:
            notification_data = NotificationCreate(
                user_id=user_id,
                notification_type=NotificationType.EMAIL.value,
                category=NotificationCategory.SESSION_REMINDER.value,
                template_id=template.id,
                template_variables=session_details
            )
        else:
            # Fallback
            session_time = session_details.get('session_time', 'your upcoming session')
            notification_data = NotificationCreate(
                user_id=user_id,
                notification_type=NotificationType.EMAIL.value,
                category=NotificationCategory.SESSION_REMINDER.value,
                subject="Session Reminder",
                body=f"Reminder: You have a training session scheduled for {session_time}."
            )
        
        return self.create_notification(db, notification_data)
    
    def send_program_assigned_notification(self, db: Session, user_id: int, program_name: str) -> Notification:
        """Send program assigned notification."""
        notification_data = NotificationCreate(
            user_id=user_id,
            notification_type=NotificationType.EMAIL.value,
            category=NotificationCategory.PROGRAM_ASSIGNED.value,
            subject="New Training Program Assigned",
            body=f"You have been assigned a new training program: {program_name}. Check your dashboard to view the details."
        )
        
        return self.create_notification(db, notification_data)
    
    def send_welcome_notification(self, db: Session, user_id: int, user_name: str) -> Notification:
        """Send welcome notification to new users."""
        notification_data = NotificationCreate(
            user_id=user_id,
            notification_type=NotificationType.EMAIL.value,
            category=NotificationCategory.WELCOME.value,
            subject="Welcome to FitnessPR!",
            body=f"Welcome {user_name}! We're excited to help you achieve your fitness goals. Get started by exploring your personalized dashboard."
        )
        
        return self.create_notification(db, notification_data)
    
    def send_session_cancelled_notification(self, db: Session, user_id: int, cancellation_details: Dict[str, Any]) -> Notification:
        """Send session cancelled notification."""
        template = self.get_template_by_name(db, "session_cancelled")
        
        if template:
            notification_data = NotificationCreate(
                user_id=user_id,
                notification_type=NotificationType.EMAIL.value,
                category=NotificationCategory.SESSION_CANCELLED.value,
                template_id=template.id,
                template_variables=cancellation_details
            )
        else:
            # Fallback
            session_date = cancellation_details.get('session_date', 'your session')
            reason = cancellation_details.get('cancellation_reason', 'scheduling conflict')
            notification_data = NotificationCreate(
                user_id=user_id,
                notification_type=NotificationType.EMAIL.value,
                category=NotificationCategory.SESSION_CANCELLED.value,
                subject=f"Session Cancelled - {session_date}",
                body=f"Your session scheduled for {session_date} has been cancelled. Reason: {reason}"
            )
        
        return self.create_notification(db, notification_data)
    
    def send_session_rescheduled_notification(self, db: Session, user_id: int, reschedule_details: Dict[str, Any]) -> Notification:
        """Send session rescheduled notification."""
        session_time = reschedule_details.get('session_time', 'your session')
        reason = reschedule_details.get('reschedule_reason', 'scheduling change')
        
        notification_data = NotificationCreate(
            user_id=user_id,
            notification_type=NotificationType.EMAIL.value,
            category=NotificationCategory.SESSION_RESCHEDULED.value,
            subject=f"Session Rescheduled - {session_time}",
            body=f"Your session has been rescheduled to {session_time}. Reason: {reason}. Please update your calendar accordingly."
        )
        
        return self.create_notification(db, notification_data)
    
    def send_group_session_booking_notification(self, db: Session, user_id: int, session_details: Dict[str, Any]) -> Notification:
        """Send group session booking confirmation."""
        session_title = session_details.get('session_title', 'Group Session')
        session_date = session_details.get('session_date', 'your session')
        status = session_details.get('status', 'confirmed')
        
        if status == "waitlisted":
            subject = f"Waitlisted for {session_title}"
            body = f"You have been added to the waitlist for {session_title} on {session_date}. We'll notify you if a spot becomes available."
        else:
            subject = f"Booking Confirmed: {session_title}"
            body = f"Your booking for {session_title} on {session_date} has been confirmed. See you there!"
        
        notification_data = NotificationCreate(
            user_id=user_id,
            notification_type=NotificationType.EMAIL.value,
            category=NotificationCategory.SESSION_REMINDER.value,
            subject=subject,
            body=body
        )
        
        return self.create_notification(db, notification_data)
    
    def send_waitlist_promotion_notification(self, db: Session, user_id: int, session_details: Dict[str, Any]) -> Notification:
        """Send notification when client is promoted from waitlist."""
        session_title = session_details.get('session_title', 'Group Session')
        session_date = session_details.get('session_date', 'your session')
        
        notification_data = NotificationCreate(
            user_id=user_id,
            notification_type=NotificationType.EMAIL.value,
            category=NotificationCategory.SESSION_REMINDER.value,
            subject=f"Spot Available: {session_title}",
            body=f"Great news! A spot has opened up for {session_title} on {session_date}. Your booking is now confirmed!"
        )
        
        return self.create_notification(db, notification_data)
    
    # ============ NOTIFICATION HISTORY ============
    
    def get_user_notifications(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50,
        category: Optional[str] = None,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if category:
            query = query.filter(Notification.category == category)
        
        if unread_only:
            query = query.filter(Notification.read_at.is_(None))
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def mark_notification_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification and not notification.read_at:
            notification.read_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    def get_notification_stats(self, db: Session, user_id: Optional[int] = None) -> Dict[str, int]:
        """Get notification statistics."""
        query = db.query(Notification)
        
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        
        total = query.count()
        sent = query.filter(Notification.status == NotificationStatus.SENT.value).count()
        delivered = query.filter(Notification.status == NotificationStatus.DELIVERED.value).count()
        failed = query.filter(Notification.status == NotificationStatus.FAILED.value).count()
        read = query.filter(Notification.read_at.isnot(None)).count()
        pending = query.filter(Notification.status == NotificationStatus.PENDING.value).count()
        
        return {
            "total_notifications": total,
            "sent_notifications": sent,
            "delivered_notifications": delivered,
            "failed_notifications": failed,
            "read_notifications": read,
            "pending_notifications": pending
        }

    def get_notification_by_id(self, db: Session, notification_id: int) -> Optional[Notification]:
        """Get notification by ID."""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification

    def mark_notification_as_read(self, db: Session, notification_id: int, user_id: int) -> Notification:
        """Mark notification as read."""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
        return notification

    def delete_notification(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Delete notification."""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        db.delete(notification)
        db.commit()
        return True

    def _send_email_notification(self, to_email: str, subject: str, body: str) -> bool:
        """Send email notification."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def get_pending_notifications(self, db: Session) -> List[Notification]:
        """Get all pending notifications."""
        return db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING
        ).all()

    def process_scheduled_notifications(self, db: Session) -> Dict[str, int]:
        """Process scheduled notifications."""
        pending_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING,
            Notification.scheduled_for <= datetime.utcnow()
        ).all()
        
        processed = 0
        failed = 0
        
        for notification in pending_notifications:
            try:
                # Use asyncio to run the async method
                success = asyncio.run(self._send_notification(db, notification))
                if success:
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Failed to process notification {notification.id}: {e}")
                failed += 1
        
        return {
            "processed": processed,
            "failed": failed,
            "total": len(pending_notifications)
        }

    def bulk_create_notifications(self, db: Session, notifications_data: List[NotificationCreate]) -> List[Notification]:
        """Create multiple notifications in bulk."""
        notifications = []
        for notification_data in notifications_data:
            notification = self.create_notification(db, notification_data)
            notifications.append(notification)
        return notifications


# Global notification service instance
notification_service = NotificationService()