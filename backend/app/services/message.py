"""
Message service for fetching, normalizing, and storing messages
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.schemas.message import NormalizedMessage, MessageFilters, ThreadContext
from app.models.message import Message
from app.models.platform import PlatformConnection
from app.integrations.interfaces import PlatformInterface, RawMessage
from app.integrations.google.gmail import GoogleGmailAdapter
from app.utils.database import transaction_scope, safe_commit, safe_rollback
from app.utils.token_refresh import needs_refresh

logger = logging.getLogger(__name__)


class MessageService:
    """Service for managing message fetching, normalization, and storage"""
    
    def __init__(self):
        """Initialize the message service with platform adapters"""
        self._adapters: Optional[Dict[str, PlatformInterface]] = None
    
    @property
    def adapters(self) -> Dict[str, PlatformInterface]:
        """Lazy-load platform adapters only when needed"""
        if self._adapters is None:
            from app.core.config import settings
            self._adapters = {}
            
            # Gmail adapter
            if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
                self._adapters["gmail"] = GoogleGmailAdapter(
                    settings.GOOGLE_CLIENT_ID,
                    settings.GOOGLE_CLIENT_SECRET
                )
        return self._adapters
    
    async def fetch_new_messages(
        self,
        user_id: UUID,
        db: Session,
        platform: Optional[str] = None
    ) -> List[NormalizedMessage]:
        """
        Fetch new messages from connected platforms for a user.
        
        Args:
            user_id: User ID to fetch messages for
            db: Database session
            platform: Optional specific platform to fetch from (gmail, slack, calendar)
        
        Returns:
            List of normalized messages
        """
        normalized_messages = []
        
        # Get connected platforms for this user
        query = db.query(PlatformConnection).filter(PlatformConnection.user_id == user_id)
        if platform:
            query = query.filter(PlatformConnection.platform == platform)
        
        connections = query.all()
        
        for connection in connections:
            try:
                # Check if token needs refresh and refresh it
                if needs_refresh(connection):
                    logger.info(f"Token expired for {connection.platform}, attempting refresh...")
                    try:
                        # Get the appropriate adapter
                        adapter = self.adapters.get(connection.platform)
                        if not adapter:
                            logger.warning(f"No adapter found for platform: {connection.platform}")
                            continue
                        
                        # Refresh the token
                        new_connection = await adapter.refresh_token(
                            user_id=str(user_id),
                            refresh_token=connection.refresh_token
                        )
                        
                        # Update connection with new tokens
                        connection.access_token = new_connection.access_token
                        if new_connection.refresh_token:
                            connection.refresh_token = new_connection.refresh_token
                        if new_connection.token_expires_at:
                            connection.token_expires_at = new_connection.token_expires_at
                        
                        db.commit()
                        logger.info(f"Successfully refreshed token for {connection.platform}")
                        
                    except Exception as refresh_error:
                        logger.error(
                            f"Failed to refresh token for {connection.platform}: {str(refresh_error)}. "
                            f"User needs to re-authenticate."
                        )
                        continue
                
                # Get the appropriate adapter
                adapter = self.adapters.get(connection.platform)
                if not adapter:
                    logger.warning(f"No adapter found for platform: {connection.platform}")
                    continue
                
                # Fetch messages since last sync
                since = connection.last_sync_at
                raw_messages = await adapter.fetch_messages(
                    user_id=str(user_id),
                    access_token=connection.access_token,
                    refresh_token=connection.refresh_token,
                    since=since
                )
                
                logger.info(
                    f"Fetched {len(raw_messages)} messages from {connection.platform} "
                    f"for user {user_id}"
                )
                
                # Normalize each message
                for raw_msg in raw_messages:
                    try:
                        normalized = self.normalize_message(
                            raw_message=raw_msg,
                            user_id=user_id,
                            platform=connection.platform
                        )
                        normalized_messages.append(normalized)
                    except Exception as e:
                        logger.error(
                            f"Failed to normalize message {raw_msg.platform_message_id}: {str(e)}"
                        )
                        continue
                
                # Update last sync time
                connection.last_sync_at = datetime.now()
                db.commit()
                
            except Exception as e:
                logger.error(
                    f"Failed to fetch messages from {connection.platform} "
                    f"for user {user_id}: {str(e)}"
                )
                continue
        
        return normalized_messages
    
    def normalize_message(
        self,
        raw_message: RawMessage,
        user_id: UUID,
        platform: str
    ) -> NormalizedMessage:
        """
        Normalize a raw message from any platform to unified format.
        
        Args:
            raw_message: Raw message data from platform
            user_id: User ID who owns this message
            platform: Platform identifier ('gmail', 'slack', 'calendar')
        
        Returns:
            NormalizedMessage with unified format
        """
        return NormalizedMessage(
            user_id=user_id,
            platform=platform,
            platform_message_id=raw_message.platform_message_id,
            sender=raw_message.sender,
            content=raw_message.content,
            subject=raw_message.subject,
            timestamp=raw_message.timestamp,
            thread_id=raw_message.thread_id,
            metadata=raw_message.metadata
        )
    
    def store_message(
        self,
        message: NormalizedMessage,
        db: Session
    ) -> str:
        """
        Store a normalized message in the database with transaction handling.
        
        Args:
            message: Normalized message to store
            db: Database session
        
        Returns:
            Message ID (UUID as string)
        
        Raises:
            IntegrityError: If message already exists (duplicate)
        
        Validates: Requirements 16.4
        """
        try:
            with transaction_scope(
                db,
                user_id=str(message.user_id),
                operation=f"store_message_{message.platform}"
            ):
                # Create message model
                db_message = Message(
                    user_id=message.user_id,
                    platform=message.platform,
                    platform_message_id=message.platform_message_id,
                    sender=message.sender,
                    content=message.content,
                    subject=message.subject,
                    timestamp=message.timestamp,
                    thread_id=message.thread_id,
                    platform_metadata=message.metadata
                )
                
                db.add(db_message)
                # Commit happens in transaction_scope
            
            db.refresh(db_message)
            logger.info(f"Stored message {db_message.id} from {message.platform}")
            return str(db_message.id)
            
        except IntegrityError as e:
            # Message already exists (duplicate detection)
            logger.debug(
                f"Duplicate message detected: {message.platform_message_id} "
                f"from {message.platform}"
            )
            # Get existing message ID
            existing = db.query(Message).filter(
                Message.user_id == message.user_id,
                Message.platform == message.platform,
                Message.platform_message_id == message.platform_message_id
            ).first()
            return str(existing.id) if existing else None
    
    def get_messages(
        self,
        user_id: UUID,
        db: Session,
        filters: Optional[MessageFilters] = None
    ) -> List[Message]:
        """
        Get messages for a user with optional filters.
        
        Args:
            user_id: User ID to get messages for
            db: Database session
            filters: Optional filters to apply
        
        Returns:
            List of Message models
        """
        query = db.query(Message).filter(Message.user_id == user_id)
        
        if filters:
            if filters.platform:
                query = query.filter(Message.platform == filters.platform)
            if filters.start_date:
                query = query.filter(Message.timestamp >= filters.start_date)
            if filters.end_date:
                query = query.filter(Message.timestamp <= filters.end_date)
            
            # Order by timestamp descending
            query = query.order_by(Message.timestamp.desc())
            
            # Apply pagination
            query = query.offset(filters.offset).limit(filters.limit)
        else:
            query = query.order_by(Message.timestamp.desc()).limit(50)
        
        return query.all()
    
    def get_thread_context(
        self,
        message_id: UUID,
        db: Session
    ) -> Optional[ThreadContext]:
        """
        Get full thread context for a message.
        
        Args:
            message_id: Message ID to get thread for
            db: Database session
        
        Returns:
            ThreadContext with all messages in the thread, or None if not found
        """
        # Get the original message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message or not message.thread_id:
            return None
        
        # Get all messages in the thread
        thread_messages = db.query(Message).filter(
            Message.thread_id == message.thread_id,
            Message.user_id == message.user_id
        ).order_by(Message.timestamp.asc()).all()
        
        if not thread_messages:
            return None
        
        # Convert to NormalizedMessage schemas
        normalized_messages = [
            NormalizedMessage(
                id=msg.id,
                user_id=msg.user_id,
                platform=msg.platform,
                platform_message_id=msg.platform_message_id,
                sender=msg.sender,
                content=msg.content,
                subject=msg.subject,
                timestamp=msg.timestamp,
                thread_id=msg.thread_id,
                metadata=msg.platform_metadata or {}
            )
            for msg in thread_messages
        ]
        
        # Count unique participants
        participants = set(msg.sender for msg in thread_messages)
        
        return ThreadContext(
            thread_id=message.thread_id,
            messages=normalized_messages,
            participant_count=len(participants),
            start_time=thread_messages[0].timestamp,
            last_update=thread_messages[-1].timestamp
        )
