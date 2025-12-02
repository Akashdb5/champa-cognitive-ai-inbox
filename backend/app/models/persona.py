"""
User persona model
"""
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class UserPersona(Base):
    __tablename__ = "user_persona"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_key = Column(String(255), nullable=False)
    memory_value = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'memory_key', name='uq_user_memory_key'),
    )
    
    # Relationships
    user = relationship("User", back_populates="persona_memories")
