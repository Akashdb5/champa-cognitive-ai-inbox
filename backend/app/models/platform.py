"""
Platform connection model
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)  # 'gmail', 'slack', 'calendar'
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(TIMESTAMP, nullable=True)
    connected_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    last_sync_at = Column(TIMESTAMP, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='uq_user_platform'),
    )
    
    # Relationships
    user = relationship("User", back_populates="platform_connections")
