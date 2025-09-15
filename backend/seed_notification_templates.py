"""
Seed script for creating default notification templates.
Run this after database migration to populate initial templates.
"""

from sqlalchemy.orm import Session
from app.session import SessionLocal
from app.models.notification import NotificationTemplate, NotificationType, NotificationCategory


def create_default_templates():
    """Create default notification templates."""
    db = SessionLocal()
    
    try:
        templates = [
            {
                "name": "client_pin_generated",
                "category": NotificationCategory.PIN_GENERATED.value,
                "notification_type": NotificationType.EMAIL.value,
                "subject": "Your FitnessPR Access PIN",
                "title": "Access PIN Generated",
                "body": """
Hello!

Your FitnessPR access PIN has been generated: {pin_code}

Use this PIN to access your personalized fitness dashboard where you can:
- View your training programs
- Track your progress
- Access meal plans
- Book sessions with your trainer

Your PIN is valid for 1 year and should be kept secure.

Best regards,
The FitnessPR Team
                """,
                "variables": ["pin_code"],
                "is_system_template": True
            },
            {
                "name": "session_reminder",
                "category": NotificationCategory.SESSION_REMINDER.value,
                "notification_type": NotificationType.EMAIL.value,
                "subject": "Session Reminder - {session_type}",
                "title": "Upcoming Session",
                "body": """
Hi there!

This is a reminder about your upcoming training session:

📅 Date & Time: {session_time}
🏋️ Session Type: {session_type}
👨‍🏫 Trainer: {trainer_name}

Please arrive 5-10 minutes early and bring:
- Water bottle
- Towel
- Appropriate workout attire

If you need to reschedule or cancel, please contact your trainer as soon as possible.

See you soon!
The FitnessPR Team
                """,
                "variables": ["session_time", "session_type", "trainer_name"],
                "is_system_template": True
            },
            {
                "name": "program_assigned",
                "category": NotificationCategory.PROGRAM_ASSIGNED.value,
                "notification_type": NotificationType.EMAIL.value,
                "subject": "New Training Program: {program_name}",
                "title": "New Program Assigned",
                "body": """
Great news!

You have been assigned a new training program: {program_name}

Your trainer has customized this program specifically for your fitness goals. 
Log in to your dashboard using your PIN to:

- View your complete workout schedule
- See exercise instructions and videos
- Track your progress
- Log your workouts

Remember to stay consistent and reach out to your trainer if you have any questions!

Keep pushing towards your goals!
The FitnessPR Team
                """,
                "variables": ["program_name"],
                "is_system_template": True
            },
            {
                "name": "welcome_client",
                "category": NotificationCategory.WELCOME.value,
                "notification_type": NotificationType.EMAIL.value,
                "subject": "Welcome to FitnessPR!",
                "title": "Welcome!",
                "body": """
Welcome to FitnessPR, {user_name}!

We're thrilled to have you join our fitness community. Your journey to better health and fitness starts now!

Here's what you can expect:
✅ Personalized training programs
✅ Expert guidance from certified trainers
✅ Progress tracking and analytics
✅ Customized meal plans
✅ 24/7 access to your fitness dashboard

Your trainer will be in touch soon to get you started. In the meantime, keep an eye out for your access PIN which will allow you to log into your personal dashboard.

Ready to transform your life? Let's do this!

The FitnessPR Team
                """,
                "variables": ["user_name"],
                "is_system_template": True
            },
            {
                "name": "session_cancelled",
                "category": NotificationCategory.SESSION_CANCELLED.value,
                "notification_type": NotificationType.EMAIL.value,
                "subject": "Session Cancelled - {session_date}",
                "title": "Session Cancelled",
                "body": """
Hi there,

We're writing to inform you that your training session scheduled for {session_date} has been cancelled.

Reason: {cancellation_reason}

Your trainer will reach out shortly to reschedule. We apologize for any inconvenience this may cause.

If you have any questions, please don't hesitate to contact us.

Best regards,
The FitnessPR Team
                """,
                "variables": ["session_date", "cancellation_reason"],
                "is_system_template": True
            },
            {
                "name": "meal_plan_assigned",
                "category": NotificationCategory.MEAL_PLAN_ASSIGNED.value,
                "notification_type": NotificationType.EMAIL.value,
                "subject": "New Meal Plan: {meal_plan_name}",
                "title": "New Meal Plan",
                "body": """
Hello!

Great news! Your trainer has created a personalized meal plan for you: {meal_plan_name}

This meal plan has been designed to complement your training program and help you achieve your nutrition goals.

Access your meal plan using your PIN to:
- View detailed recipes and ingredients
- See nutritional information
- Track your meal adherence
- Get shopping lists

Nutrition is 70% of your fitness journey - let's make it count!

The FitnessPR Team
                """,
                "variables": ["meal_plan_name"],
                "is_system_template": True
            }
        ]
        
        for template_data in templates:
            # Check if template already exists
            existing = db.query(NotificationTemplate).filter(
                NotificationTemplate.name == template_data["name"]
            ).first()
            
            if not existing:
                template = NotificationTemplate(**template_data)
                db.add(template)
                print(f"Created template: {template_data['name']}")
            else:
                print(f"Template already exists: {template_data['name']}")
        
        db.commit()
        print("Default notification templates created successfully!")
        
    except Exception as e:
        print(f"Error creating templates: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_default_templates()
