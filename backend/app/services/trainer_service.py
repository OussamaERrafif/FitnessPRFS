from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from app.models.trainer import Trainer, TrainerCertification, TrainerAvailability
from app.models.client import Client
from app.models.user import User
from app.models.session_booking import SessionBooking, SessionStatus
from app.schemas.trainer import (
    TrainerCreate,
    TrainerUpdate,
    TrainerResponse,
    TrainerCertificationCreate,
    TrainerCertificationUpdate,
    TrainerAvailabilityCreate,
    TrainerAvailabilityUpdate,
    TrainerStats,
    TrainerDashboard
)


class TrainerService:
    """Service for trainer-related operations."""
    
    @staticmethod
    def create_trainer(db: Session, trainer_data: TrainerCreate) -> Trainer:
        """Create a new trainer profile."""
        # Check if trainer profile already exists for this user
        existing_trainer = db.query(Trainer).filter(Trainer.user_id == trainer_data.user_id).first()
        if existing_trainer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trainer profile already exists for this user"
            )
        
        trainer_dict = trainer_data.model_dump()
        
        # Convert lists to JSON strings
        if trainer_dict.get('specializations'):
            trainer_dict['specializations'] = str(trainer_dict['specializations'])
        
        trainer = Trainer(**trainer_dict)
        
        db.add(trainer)
        db.commit()
        db.refresh(trainer)
        return trainer
    
    @staticmethod
    def get_trainer_by_id(db: Session, trainer_id: int, include_inactive: bool = False) -> Optional[Trainer]:
        """Get trainer by ID."""
        query = db.query(Trainer).filter(Trainer.id == trainer_id)
        if not include_inactive:
            query = query.filter(Trainer.is_active == True)
        return query.first()
    
    @staticmethod
    def get_trainer_by_user_id(db: Session, user_id: int) -> Optional[Trainer]:
        """Get trainer by user ID."""
        return db.query(Trainer).filter(Trainer.user_id == user_id).first()
    
    @staticmethod
    def get_all_trainers(
        db: Session, 
        skip: int = 0, 
        limit: int = 50,
        is_active: Optional[bool] = None
    ) -> List[Trainer]:
        """Get all trainers with optional filtering."""
        query = db.query(Trainer)
        
        if is_active is not None:
            query = query.filter(Trainer.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_trainer(db: Session, trainer_id: int, trainer_data: TrainerUpdate) -> Optional[Trainer]:
        """Update trainer profile."""
        trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
        if not trainer:
            return None
        
        update_dict = trainer_data.model_dump(exclude_unset=True)
        
        # Convert lists to JSON strings
        if 'specializations' in update_dict and update_dict['specializations']:
            update_dict['specializations'] = str(update_dict['specializations'])
        
        for field, value in update_dict.items():
            setattr(trainer, field, value)
        
        trainer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(trainer)
        return trainer
    
    @staticmethod
    def add_certification(
        db: Session, 
        trainer_id: int, 
        cert_data: TrainerCertificationCreate
    ) -> Optional[TrainerCertification]:
        """Add a certification to a trainer."""
        trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
        if not trainer:
            return None
        
        certification = TrainerCertification(
            trainer_id=trainer_id,
            **cert_data.model_dump()
        )
        
        db.add(certification)
        db.commit()
        db.refresh(certification)
        return certification
    
    @staticmethod
    def update_certification(
        db: Session, 
        certification_id: int, 
        cert_data: TrainerCertificationUpdate
    ) -> Optional[TrainerCertification]:
        """Update a trainer certification."""
        certification = db.query(TrainerCertification).filter(
            TrainerCertification.id == certification_id
        ).first()
        
        if not certification:
            return None
        
        update_dict = cert_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(certification, field, value)
        
        db.commit()
        db.refresh(certification)
        return certification
    
    @staticmethod
    def get_trainer_certifications(db: Session, trainer_id: int) -> List[TrainerCertification]:
        """Get all certifications for a trainer."""
        return db.query(TrainerCertification).filter(
            TrainerCertification.trainer_id == trainer_id
        ).all()
    
    @staticmethod
    def set_availability(
        db: Session, 
        trainer_id: int, 
        availability_data: TrainerAvailabilityCreate
    ) -> Optional[TrainerAvailability]:
        """Set trainer availability for a specific day."""
        trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
        if not trainer:
            return None
        
        # Check if availability already exists for this day
        existing = db.query(TrainerAvailability).filter(
            and_(
                TrainerAvailability.trainer_id == trainer_id,
                TrainerAvailability.day_of_week == availability_data.day_of_week
            )
        ).first()
        
        if existing:
            # Update existing availability
            update_dict = availability_data.model_dump()
            for field, value in update_dict.items():
                setattr(existing, field, value)
            
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new availability
            availability = TrainerAvailability(
                trainer_id=trainer_id,
                **availability_data.model_dump()
            )
            
            db.add(availability)
            db.commit()
            db.refresh(availability)
            return availability
    
    @staticmethod
    def get_trainer_availability(db: Session, trainer_id: int) -> List[TrainerAvailability]:
        """Get trainer availability schedule."""
        return db.query(TrainerAvailability).filter(
            TrainerAvailability.trainer_id == trainer_id
        ).order_by(TrainerAvailability.day_of_week).all()
    
    @staticmethod
    def get_trainer_clients(db: Session, trainer_id: int, skip: int = 0, limit: int = 50) -> List[Client]:
        """Get all clients assigned to a trainer."""
        return db.query(Client).filter(
            Client.assigned_trainer_id == trainer_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_trainer_sessions(
        db: Session, 
        trainer_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[SessionStatus] = None
    ) -> List[SessionBooking]:
        """Get trainer sessions with optional filtering."""
        query = db.query(SessionBooking).filter(
            SessionBooking.trainer_id == trainer_id
        )
        
        if start_date:
            query = query.filter(SessionBooking.scheduled_start >= start_date)
        
        if end_date:
            query = query.filter(SessionBooking.scheduled_start <= end_date)
        
        if status:
            query = query.filter(SessionBooking.status == status)
        
        return query.order_by(SessionBooking.scheduled_start).all()
    
    @staticmethod
    def get_trainer_stats(db: Session, trainer_id: int) -> TrainerStats:
        """Get trainer statistics."""
        # Total clients
        total_clients = db.query(func.count(Client.id)).filter(
            Client.assigned_trainer_id == trainer_id
        ).scalar() or 0
        
        # Active clients (have had a session in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_clients = db.query(func.count(func.distinct(SessionBooking.client_id))).filter(
            and_(
                SessionBooking.trainer_id == trainer_id,
                SessionBooking.scheduled_start >= thirty_days_ago,
                SessionBooking.status.in_([SessionStatus.COMPLETED.value, SessionStatus.CONFIRMED.value])
            )
        ).scalar() or 0
        
        # Total sessions this month
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        sessions_this_month = db.query(func.count(SessionBooking.id)).filter(
            and_(
                SessionBooking.trainer_id == trainer_id,
                SessionBooking.scheduled_start >= start_of_month,
                SessionBooking.status != SessionStatus.CANCELLED.value
            )
        ).scalar() or 0
        
        # Revenue this month (mock calculation)
        revenue_this_month = sessions_this_month * 75.0  # Assuming $75 per session
        
        # Average rating (mock - would need actual rating system)
        average_rating = 4.5
        
        return TrainerStats(
            total_clients=total_clients,
            active_clients=active_clients,
            sessions_this_month=sessions_this_month,
            revenue_this_month=revenue_this_month,
            average_rating=average_rating,
            total_sessions=sessions_this_month * 3,  # Mock total
            certification_count=len(TrainerService.get_trainer_certifications(db, trainer_id))
        )
    
    @staticmethod
    def get_trainer_dashboard(db: Session, trainer_id: int) -> TrainerDashboard:
        """Get trainer dashboard data."""
        trainer = TrainerService.get_trainer_by_id(db, trainer_id)
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        
        stats = TrainerService.get_trainer_stats(db, trainer_id)
        
        # Get today's sessions
        today = datetime.utcnow().date()
        today_sessions = db.query(SessionBooking).filter(
            and_(
                SessionBooking.trainer_id == trainer_id,
                func.date(SessionBooking.scheduled_start) == today
            )
        ).order_by(SessionBooking.scheduled_start).all()
        
        # Get upcoming sessions (next 7 days)
        next_week = datetime.utcnow() + timedelta(days=7)
        upcoming_sessions = db.query(SessionBooking).filter(
            and_(
                SessionBooking.trainer_id == trainer_id,
                SessionBooking.scheduled_start > datetime.utcnow(),
                SessionBooking.scheduled_start <= next_week,
                SessionBooking.status.in_([SessionStatus.CONFIRMED.value, SessionStatus.SCHEDULED.value])
            )
        ).order_by(SessionBooking.scheduled_start).limit(10).all()
        
        # Get recent clients
        recent_clients = db.query(Client).filter(
            Client.assigned_trainer_id == trainer_id
        ).order_by(Client.created_at.desc()).limit(5).all()
        
        return TrainerDashboard(
            trainer_info=trainer,
            stats=stats,
            today_sessions=today_sessions,
            upcoming_sessions=upcoming_sessions,
            recent_clients=recent_clients,
            notifications=[]  # Mock notifications
        )
    
    @staticmethod
    def search_trainers(
        db: Session,
        specialization: Optional[str] = None,
        location: Optional[str] = None,
        min_experience: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Trainer]:
        """Search trainers by criteria."""
        query = db.query(Trainer).filter(Trainer.is_active == True)
        
        if specialization:
            query = query.filter(Trainer.specializations.contains(specialization))
        
        if location:
            query = query.filter(
                or_(
                    Trainer.location.ilike(f"%{location}%"),
                    Trainer.bio.ilike(f"%{location}%")
                )
            )
        
        if min_experience:
            query = query.filter(Trainer.years_of_experience >= min_experience)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_trainer(db: Session, trainer_id: int) -> bool:
        """Delete a trainer (soft delete by setting is_active=False)."""
        trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
        if not trainer:
            return False
        
        # Soft delete - just mark as inactive
        trainer.is_active = False
        trainer.updated_at = datetime.utcnow()
        
        db.commit()
        return True


# Global trainer service instance
trainer_service = TrainerService()
