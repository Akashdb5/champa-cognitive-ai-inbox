"""
Message and related models
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Float, Boolean, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    platform_message_id = Column(String(255), nullable=False)
    sender = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    subject = Column(String(500), nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    thread_id = Column(String(255), nullable=True)
    platform_metadata = Column(JSONB, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy reserved name
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', 'platform_message_id', name='uq_user_platform_message'),
        Index('idx_messages_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_messages_thread', 'thread_id'),
    )
    
    # Relationships
    user = relationship("User", back_populates="messages")
    analysis = relationship("MessageAnalysis", back_populates="message", uselist=False, cascade="all, delete-orphan")
    actionable_items = relationship("ActionableItem", back_populates="message", cascade="all, delete-orphan")
    smart_replies = relationship("SmartReply", back_populates="message", cascade="all, delete-orphan")


class MessageAnalysis(Base):
    __tablename__ = "message_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    priority_score = Column(Float, nullable=False)
    is_spam = Column(Boolean, nullable=False, default=False)
    spam_score = Column(Float, nullable=False, default=0.0)
    spam_type = Column(String(50), nullable=False, default='none')
    unsubscribe_link = Column(Text, nullable=True)
    analyzed_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    message = relationship("Message", back_populates="analysis")


class ActionableItem(Base):
    __tablename__ = "actionable_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # 'task', 'deadline', 'meeting'
    description = Column(Text, nullable=False)
    deadline = Column(TIMESTAMP, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_actionables_user_deadline', 'user_id', 'deadline'),
    )
    
    # Relationships
    message = relationship("Message", back_populates="actionable_items")
    user = relationship("User", back_populates="actionable_items")


class SmartReply(Base):
    __tablename__ = "smart_replies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    draft_content = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # 'pending', 'approved', 'rejected', 'sent'
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    reviewed_at = Column(TIMESTAMP, nullable=True)
    sent_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    message = relationship("Message", back_populates="smart_replies")
    user = relationship("User", back_populates="smart_replies")
