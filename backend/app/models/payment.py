from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class PaymentStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIAL_REFUND = "partial_refund"


class PaymentMethod(PyEnum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    OTHER = "other"


class PaymentType(PyEnum):
    SESSION = "session"
    PROGRAM = "program"
    MEAL_PLAN = "meal_plan"
    SUBSCRIPTION = "subscription"
    PACKAGE = "package"
    OTHER = "other"


class Payment(Base):
    """Payment model for handling transactions."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Parties involved
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Related entities
    session_id = Column(Integer, ForeignKey("session_bookings.id"), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=True)
    
    # Payment gateway details
    transaction_id = Column(String(255), unique=True, nullable=True)
    gateway_reference = Column(String(255), nullable=True)
    gateway_response = Column(Text, nullable=True)  # JSON response from gateway
    
    # Description and notes
    description = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Discount and fees
    discount_amount = Column(Float, default=0.0)
    discount_code = Column(String(50), nullable=True)
    processing_fee = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=True)  # amount after fees
    
    # Refund information
    refund_amount = Column(Float, default=0.0)
    refund_reason = Column(String(500), nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("User", foreign_keys=[client_id])
    trainer = relationship("Trainer", backref="payments_received")
    session = relationship("SessionBooking", backref="payments")
    program = relationship("Program", backref="payments")
    meal_plan = relationship("MealPlan", backref="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"


class Subscription(Base):
    """Subscription model for recurring payments."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Subscription details
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    
    # Plan details
    plan_name = Column(String(255), nullable=False)
    plan_type = Column(String(100), nullable=False)  # weekly, monthly, yearly
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    billing_cycle_days = Column(Integer, nullable=False)  # 7, 30, 365, etc.
    
    # Status and dates
    status = Column(String(50), default="active")  # active, paused, cancelled
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    
    # Payment details
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    gateway_subscription_id = Column(String(255), nullable=True)
    
    # Included services
    sessions_per_cycle = Column(Integer, nullable=True)
    programs_included = Column(Boolean, default=False)
    meal_plans_included = Column(Boolean, default=False)
    
    # Usage tracking
    sessions_used_current_cycle = Column(Integer, default=0)
    cycle_start_date = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("User", foreign_keys=[client_id])
    trainer = relationship("Trainer", backref="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, client_id={self.client_id}, status='{self.status}')>"
