"""
Models package for FitnessPR API.

This package contains all SQLAlchemy models for the application.
"""

from app.models.user import User, UserRole
from app.models.client import Client, ActivityLevel, FitnessGoal
from app.models.trainer import Trainer, TrainerCertification, TrainerAvailability
from app.models.cancellation import CancellationPolicy, TrainerAvailabilitySlot
from app.models.group_session import GroupSession, GroupSessionType
from app.models.exercise import (
    Exercise, 
    ExerciseCategory, 
    MuscleGroup, 
    EquipmentType, 
    DifficultyLevel
)
from app.models.progress_log import (
    ProgressLog, 
    WorkoutType, 
    IntensityLevel
)
from app.models.program import (
    Program, 
    ProgramType, 
    ProgramDifficulty, 
    ProgramStatus
)
from app.models.session_booking import (
    SessionBooking, 
    SessionType, 
    SessionStatus
)
from app.models.meal_plan import (
    MealPlan, 
    MealPlanRecipe,
    MealPlanType, 
    DietaryRestriction,
    MealType,
    DietType
)
from app.models.recipe import Recipe
from app.models.payment import (
    Payment, 
    Subscription, 
    PaymentStatus, 
    PaymentMethod, 
    PaymentType
)
from app.models.refresh_token import RefreshToken, ClientPINToken
from app.models.attachment import (
    Attachment, 
    AttachmentType, 
    AttachmentCategory
)

__all__ = [
    # User models
    "User",
    "UserRole",
    "Client",
    "ActivityLevel",
    "FitnessGoal",
    "Trainer",
    "TrainerCertification",
    "TrainerAvailability",
    "CancellationPolicy",
    "TrainerAvailabilitySlot",
    "GroupSession",
    "GroupSessionType",
    
    # Exercise and progress models
    "Exercise",
    "ExerciseCategory",
    "MuscleGroup",
    "EquipmentType",
    "DifficultyLevel",
    "ProgressLog",
    "WorkoutType",
    "IntensityLevel",
    
    # Program models
    "Program",
    "ProgramType",
    "ProgramDifficulty",
    "ProgramStatus",
    
    # Session models
    "SessionBooking",
    "SessionType",
    "SessionStatus",
    
    # Meal plan models
    "MealPlan",
    "MealPlanType",
    "DietaryRestriction",
    "Recipe",
    
    # Payment models
    "Payment",
    "Subscription",
    "PaymentStatus",
    "PaymentMethod",
    "PaymentType",
    
    # Token models
    "RefreshToken",
    "ClientPINToken",
    
    # Attachment models
    "Attachment",
    "AttachmentType",
    "AttachmentCategory",
]
