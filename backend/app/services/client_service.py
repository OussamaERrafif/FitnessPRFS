import random
import string
from datetime import datetime, timedelta, UTC
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.client import Client
from app.models.user import User
from app.models.trainer import Trainer
from app.services.auth_service import auth_service
from app.schemas.client import (
    ClientCreate, 
    ClientUpdate, 
    ClientResponse, 
    ClientPINAccess,
    ClientPINLogin,
    ClientProfileUpdate,
    ClientStats
)


class ClientService:
    """Service for client-related operations."""
    
    @staticmethod
    def generate_pin_code() -> str:
        """Generate a unique 6-digit PIN code."""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_client(db: Session, client_data: ClientCreate) -> Client:
        """Create a new client profile."""
        # Check if client profile already exists for this user
        existing_client = db.query(Client).filter(Client.user_id == client_data.user_id).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client profile already exists for this user"
            )
        
        # Generate unique PIN code
        pin_code = ClientService.generate_pin_code()
        while db.query(Client).filter(Client.pin == pin_code).first():
            pin_code = ClientService.generate_pin_code()
        
        # Create client
        client_dict = client_data.model_dump(exclude_unset=True, exclude={'user_id'})
        
        # JSON fields are passed through directly
        
        client = Client(
            user_id=client_data.user_id,
            **client_dict,
            pin=pin_code,
            pin_expires_at=datetime.now(UTC) + timedelta(days=365),  # PIN valid for 1 year
            is_membership_active=False
        )
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        # Send PIN notification
        try:
            from app.services.notification_service import notification_service
            notification_service.send_pin_generated_notification(db, client_data.user_id, pin_code)
        except Exception as e:
            # Log error but don't fail client creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send PIN notification: {str(e)}")
        
        return client
    
    @staticmethod
    def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get list of clients with pagination."""
        return db.query(Client).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_client_by_id(db: Session, client_id: int) -> Optional[Client]:
        """Get client by ID."""
        return db.query(Client).filter(Client.id == client_id).first()
    
    @staticmethod
    def get_client_by_user_id(db: Session, user_id: int) -> Optional[Client]:
        """Get client by user ID."""
        return db.query(Client).filter(Client.user_id == user_id).first()
    
    @staticmethod
    def get_client_by_pin(db: Session, pin_code: str) -> Optional[Client]:
        """Get client by PIN code."""
        return db.query(Client).filter(
            Client.pin == pin_code,
            Client.pin_expires_at > datetime.now(UTC)
        ).first()
    
    @staticmethod
    def update_client(db: Session, client_id: int, client_data: ClientUpdate) -> Optional[Client]:
        """Update client profile."""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None
        
        update_dict = client_data.model_dump(exclude_unset=True)
        
        # JSON fields are passed through directly
        
        for field, value in update_dict.items():
            setattr(client, field, value)
        
        client.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(client)
        return client
    
    @staticmethod
    def authenticate_with_pin(db: Session, pin_access: ClientPINAccess) -> Optional[ClientPINLogin]:
        """Authenticate client with PIN code."""
        client = ClientService.get_client_by_pin(db, pin_access.pin_code)
        if not client:
            return None
        
        # Get user information
        user = db.query(User).filter(User.id == client.user_id).first()
        if not user or not user.is_active:
            return None
        
        # Create special token for PIN access
        token_data = {
            "sub": str(user.id),
            "client_id": str(client.id),
            "email": user.email,
            "role": "client_pin",
            "pin_access": True
        }
        
        access_token = auth_service.create_access_token(
            token_data, 
            expires_delta=timedelta(hours=2)  # Shorter expiry for PIN access
        )
        
        return ClientPINLogin(
            client_id=client.id,
            user_id=user.id,
            full_name=user.full_name or user.username,
            access_token=access_token,
            expires_in=2 * 60 * 60  # 2 hours in seconds
        )

    @staticmethod
    def delete_client(db: Session, client_id: int) -> bool:
        """Delete a client profile."""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return False
        db.delete(client)
        db.commit()
        return True
    
    @staticmethod
    def update_profile_via_pin(
        db: Session, 
        client_id: int, 
        profile_data: ClientProfileUpdate
    ) -> Optional[Client]:
        """Update client profile via PIN access."""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None
        
        update_dict = profile_data.model_dump(exclude_unset=True)
        
        # Convert lists to JSON strings
        if 'fitness_goals' in update_dict and update_dict['fitness_goals']:
            update_dict['fitness_goals'] = str(update_dict['fitness_goals'])
        
        # Handle notes separately - append to existing notes
        if 'notes' in update_dict and update_dict['notes']:
            timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")
            new_note = f"[{timestamp} - Client Update]: {update_dict['notes']}"
            
            # Get existing notes from user or create new
            user = db.query(User).filter(User.id == client.user_id).first()
            if user.bio:
                user.bio = f"{user.bio}\n{new_note}"
            else:
                user.bio = new_note
            
            del update_dict['notes']  # Remove from client update
        
        # Update client fields
        for field, value in update_dict.items():
            setattr(client, field, value)
        
        client.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(client)
        return client
    
    @staticmethod
    def assign_trainer(db: Session, client_id: int, trainer_id: int) -> Optional[Client]:
        """Assign a trainer to a client."""
        client = db.query(Client).filter(Client.id == client_id).first()
        trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
        
        if not client or not trainer:
            return None
        
        client.assigned_trainer_id = trainer_id
        client.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(client)
        return client
    
    @staticmethod
    def get_trainer_clients(db: Session, trainer_id: int, skip: int = 0, limit: int = 50) -> List[Client]:
        """Get all clients assigned to a trainer."""
        return db.query(Client).filter(
            Client.assigned_trainer_id == trainer_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def regenerate_pin(db: Session, client_id: int) -> Optional[str]:
        """Regenerate PIN code for a client."""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None
        
        # Generate new unique PIN
        new_pin = ClientService.generate_pin_code()
        while db.query(Client).filter(Client.pin == new_pin).first():
            new_pin = ClientService.generate_pin_code()
        
        client.pin = new_pin
        client.pin_expires_at = datetime.now(UTC) + timedelta(days=365)
        client.updated_at = datetime.now(UTC)
        
        db.commit()
        return new_pin
    
    @staticmethod
    def get_client_stats(db: Session, client_id: int) -> ClientStats:
        """Get client statistics."""
        # This is a mock implementation - you would query actual data
        return ClientStats(
            total_sessions=0,
            completed_sessions=0,
            completed_workouts=0,
            active_programs=0,
            total_workouts_logged=0,
            current_streak_days=0,
            total_weight_change=0.0,
            weight_progress=0.0
        )


# Global client service instance
client_service = ClientService()