from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class RefreshToken(Base):
    """Refresh token model for JWT authentication."""
    
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Token details
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token lifecycle
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    
    # Device and session information
    device_info = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
    
    def is_valid(self) -> bool:
        """Check if the token is still valid."""
        return not self.is_revoked and self.expires_at > datetime.utcnow()


class ClientPINToken(Base):
    """PIN-based token for client self-service access."""
    
    __tablename__ = "client_pin_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Token details
    token = Column(String(500), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # PIN information
    pin_hash = Column(String(255), nullable=False)  # Hashed PIN
    
    # Token lifecycle
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    
    # Device information
    device_info = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("Client", backref="pin_tokens")
    
    def __repr__(self):
        return f"<ClientPINToken(id={self.id}, client_id={self.client_id}, expires_at={self.expires_at})>"
    
    def is_valid(self) -> bool:
        """Check if the PIN token is still valid."""
        return not self.is_revoked and self.expires_at > datetime.utcnow()
