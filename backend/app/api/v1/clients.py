from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.client_service import client_service
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientPINAccess,
    ClientPINLogin,
    ClientProfileUpdate,
    ClientStats,
    ClientCreateInternal
)
from app.models.user import User

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0, description="Number of clients to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of clients to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all clients (for admin/trainer access)."""
    # Only trainers and admins can list all clients
    if current_user.role not in ["TRAINER", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        clients = client_service.get_clients(db, skip=skip, limit=limit)
        return [ClientResponse.model_validate(client) for client in clients]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve clients"
        )


@router.post("/", response_model=ClientResponse)
async def create_client_profile(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a client profile for a user."""
    try:
        # Create internal model with user_id from authenticated user
        client_data_internal = ClientCreateInternal(
            user_id=current_user.id,
            **client_data.model_dump()
        )
        client = client_service.create_client(db, client_data_internal)
        return ClientResponse.model_validate(client)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create client profile"
        )


@router.get("/me", response_model=ClientResponse)
async def get_my_client_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's client profile."""
    client = client_service.get_client_by_user_id(db, current_user.id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    return ClientResponse.model_validate(client)


@router.put("/me", response_model=ClientResponse)
async def update_my_client_profile(
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's client profile."""
    client = client_service.get_client_by_user_id(db, current_user.id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    updated_client = client_service.update_client(db, client.id, client_data)
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client profile"
        )
    
    return ClientResponse.model_validate(updated_client)


@router.post("/pin-access", response_model=ClientPINLogin)
async def client_pin_login(
    pin_access: ClientPINAccess,
    db: Session = Depends(get_db)
):
    """Authenticate client using PIN code."""
    try:
        login_result = client_service.authenticate_with_pin(db, pin_access)
        if not login_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN code or PIN expired"
            )
        
        return login_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PIN authentication failed"
        )


@router.put("/pin-profile/{client_id}", response_model=ClientResponse)
async def update_profile_via_pin(
    client_id: int,
    profile_data: ClientProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update client profile via PIN access (limited fields)."""
    # Verify this is PIN access
    if not getattr(current_user, 'pin_access', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires PIN access"
        )
    
    # Verify client ID matches
    if getattr(current_user, 'client_id', None) != str(client_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other client's profile"
        )
    
    updated_client = client_service.update_profile_via_pin(db, client_id, profile_data)
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return ClientResponse.model_validate(updated_client)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client_profile(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get client profile by ID (trainers and admins only)."""
    # Check if user has permission to view client profiles
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can view client profiles"
        )
    
    client = client_service.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return ClientResponse.model_validate(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client_profile(
    client_id: int,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update client profile by ID (trainers and admins only)."""
    # Check if user has permission to update client profiles
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can update client profiles"
        )
    
    updated_client = client_service.update_client(db, client_id, client_data)
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return ClientResponse.model_validate(updated_client)


@router.post("/{client_id}/assign-trainer/{trainer_id}")
async def assign_trainer_to_client(
    client_id: int,
    trainer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Assign a trainer to a client (admins only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign trainers to clients"
        )
    
    client = client_service.assign_trainer(db, client_id, trainer_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client or trainer not found"
        )
    
    return {"message": "Trainer assigned successfully"}


@router.post("/{client_id}/regenerate-pin")
async def regenerate_client_pin(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate PIN code for a client (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can regenerate PIN codes"
        )
    
    new_pin = client_service.regenerate_pin(db, client_id)
    if not new_pin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return {"message": "PIN regenerated successfully", "new_pin": new_pin}


@router.get("/{client_id}/stats", response_model=ClientStats)
async def get_client_stats(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get client statistics."""
    # Check if user has permission or is the client themselves
    client = client_service.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if (current_user.role.value not in ["trainer", "admin"] and 
        client.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other client's statistics"
        )
    
    stats = client_service.get_client_stats(db, client_id)
    return stats


@router.get("/trainer/{trainer_id}/clients", response_model=List[ClientResponse])
async def get_trainer_clients(
    trainer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all clients assigned to a trainer."""
    # Check if user is the trainer or an admin
    if current_user.role.value == "trainer":
        # Verify this trainer ID belongs to current user
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_user_id(db, current_user.id)
        if not trainer or trainer.id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other trainer's clients"
            )
    elif current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can view client lists"
        )
    
    clients = client_service.get_trainer_clients(db, trainer_id, skip, limit)
    return [ClientResponse.model_validate(client) for client in clients]
