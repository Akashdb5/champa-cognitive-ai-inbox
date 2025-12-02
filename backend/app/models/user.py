"""
User model
"""
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth0_id = Column(String(255), unique=True, nullable=False)  # Auth0 user ID (required)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # DEPRECATED: No longer used with Auth0-only auth
    
    # Profile fields
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    timezone = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    platform_connections = relationship("PlatformConnection", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    actionable_items = relationship("ActionableItem", back_populates="user", cascade="all, delete-orphan")
    smart_replies = relationship("SmartReply", back_populates="user", cascade="all, delete-orphan")
    persona_memories = relationship("UserPersona", back_populates="user", cascade="all, delete-orphan")
