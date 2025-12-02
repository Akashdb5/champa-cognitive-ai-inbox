"""
Smart Reply Service
Orchestrates smart reply generation using deep agents and persona memory.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.message import Message, SmartReply
from app.models.platform import PlatformConnection
from app.schemas.reply import SmartReply as SmartReplySchema
from app.ai.agents.deep_agent import get_smart_reply_agent
from app.ai.memory.persona_store import get_persona_store
from app.integrations.interfaces import get_platform_adapter
from langgraph.store.memory import InMemoryStore


class SmartReplyService:
    """
    Service for generating and managing smart replies.
    Implements the smart reply workflow from the design document.
    """
    
    def __init__(self, db: Session, store: Optional[InMemoryStore] = None):
        """
        Initialize smart reply service
        
        Args:
            db: Database session
            store: Optional LangGraph Store for long-term memory
        """
        self.db = db
        self.store = store or InMemoryStore()
        self.deep_agent = get_smart_reply_agent(store=self.store)
        self.persona_store = get_persona_store(db=db, store=self.store)
    
    async def fetch_thread_context(self, message_id: UUID) -> str:
        """
        Fetch complete thread context for a message
        
        Args:
            message_id: Message ID
        
        Returns:
            str: Formatted thread context
        
        Validates: Requirements 7.1
        """
        # Get the message
        message = self.db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        # Get all messages in the thread
        if message.thread_id:
            thread_messages = self.db.query(Message).filter(
                Message.thread_id == message.thread_id
            ).order_by(Message.timestamp.asc()).all()
        else:
            # Single message, no thread
            thread_messages = [message]
        
        # Format thread context
        context_lines = []
        context_lines.append(f"Platform: {message.platform}")
        context_lines.append(f"Thread ID: {message.thread_id or 'N/A'}")
        context_lines.append("")
        context_lines.append("=== Thread Messages ===")
        context_lines.append("")
        
        for msg in thread_messages:
            context_lines.append(f"From: {msg.sender}")
            context_lines.append(f"Date: {msg.timestamp.isoformat()}")
            if msg.subject:
                context_lines.append(f"Subject: {msg.subject}")
            context_lines.append(f"Content: {msg.content}")
            context_lines.append("")
            context_lines.append("---")
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    async def retrieve_persona(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user persona data for reply generation
        
        Args:
            user_id: User ID
        
        Returns:
            Dict containing persona data
        
        Validates: Requirements 7.2
        """
        return await self.persona_store.get_full_persona(user_id)
    
    async def generate_smart_reply(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> SmartReplySchema:
        """
        Generate a smart reply for a message
        
        This method:
        1. Fetches thread context
        2. Retrieves user persona
        3. Uses deep agent to plan and generate reply
        4. Formats for platform
        5. Stores as pending draft
        
        Args:
            message_id: Message ID to reply to
            user_id: User ID
        
        Returns:
            SmartReplySchema: Generated smart reply
        
        Validates: Requirements 7.1, 7.2, 7.4
        """
        # Get message
        message = self.db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        if str(message.user_id) != str(user_id):
            raise ValueError("Message does not belong to user")
        
        # Fetch thread context
        thread_context = await self.fetch_thread_context(message_id)
        
        # Retrieve persona
        persona = await self.retrieve_persona(str(user_id))
        
        # Generate reply using deep agent
        draft_content = await self.deep_agent.generate_reply(
            thread_context=thread_context,
            user_persona=persona,
            platform=message.platform,
            user_id=str(user_id)
        )
        
        # Format for platform
        formatted_draft = self._format_for_platform(
            draft_content,
            message.platform,
            message
        )
        
        # Store as pending draft
        smart_reply = SmartReply(
            message_id=message_id,
            user_id=user_id,
            draft_content=formatted_draft,
            status="pending"
        )
        
        self.db.add(smart_reply)
        self.db.commit()
        self.db.refresh(smart_reply)
        
        return SmartReplySchema.model_validate(smart_reply)
    
    def _format_for_platform(
        self,
        draft: str,
        platform: str,
        original_message: Message
    ) -> str:
        """
        Format draft reply for specific platform
        
        Args:
            draft: Raw draft content
            platform: Target platform
            original_message: Original message being replied to
        
        Returns:
            str: Formatted draft
        
        Validates: Requirements 7.4
        """
        if platform == "gmail":
            # Email formatting
            # Add Re: to subject if not already present
            subject = original_message.subject or ""
            if subject and not subject.startswith("Re:"):
                subject = f"Re: {subject}"
            
            # Draft is already formatted by the agent
            return draft
        
        elif platform == "slack":
            # Slack formatting - keep it simple
            # Agent should handle Slack-appropriate tone
            return draft
        
        elif platform == "calendar":
            # Calendar event response
            # Usually just accept/decline/tentative
            return draft
        
        return draft
    
    def get_pending_replies(self, user_id: UUID, limit: int = 50) -> list[SmartReplySchema]:
        """
        Get pending smart replies for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of replies
        
        Returns:
            List of pending smart replies
        """
        replies = self.db.query(SmartReply).filter(
            SmartReply.user_id == user_id,
            SmartReply.status == "pending"
        ).order_by(SmartReply.created_at.desc()).limit(limit).all()
        
        return [SmartReplySchema.model_validate(r) for r in replies]
    
    def get_reply(self, reply_id: UUID, user_id: UUID) -> Optional[SmartReplySchema]:
        """
        Get a specific smart reply
        
        Args:
            reply_id: Reply ID
            user_id: User ID
        
        Returns:
            SmartReplySchema if found, None otherwise
        """
        reply = self.db.query(SmartReply).filter(
            SmartReply.id == reply_id,
            SmartReply.user_id == user_id
        ).first()
        
        if reply:
            return SmartReplySchema.model_validate(reply)
        
        return None
    
    async def approve_reply(self, reply_id: UUID, user_id: UUID) -> SmartReplySchema:
        """
        Approve a smart reply and send it
        
        This implements the human-in-the-loop approval workflow.
        The user reviews the draft, and upon approval, it is sent via the platform.
        
        Args:
            reply_id: Reply ID
            user_id: User ID
        
        Returns:
            Updated smart reply
        
        Validates: Requirements 7.5, 8.1, 8.3
        """
        reply = self.db.query(SmartReply).filter(
            SmartReply.id == reply_id,
            SmartReply.user_id == user_id,
            SmartReply.status == "pending"
        ).first()
        
        if not reply:
            raise ValueError("Reply not found or not pending")
        
        # Get the original message to determine platform
        message = self.db.query(Message).filter(Message.id == reply.message_id).first()
        
        if not message:
            raise ValueError("Original message not found")
        
        # Send the reply via the appropriate platform
        try:
            await self._send_reply(message, reply.draft_content, user_id)
            
            # Mark as sent
            reply.status = "sent"
            reply.reviewed_at = datetime.utcnow()
            reply.sent_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(reply)
            
            # Record interaction for persona learning
            await self.record_interaction(
                user_id=str(user_id),
                interaction_type="reply_sent",
                interaction_data={
                    "timestamp": datetime.utcnow().isoformat(),
                    "platform": message.platform,
                    "recipient": message.sender,
                    "content_length": len(reply.draft_content)
                }
            )
            
            return SmartReplySchema.model_validate(reply)
        
        except Exception as e:
            # If sending fails, keep as approved but not sent
            reply.status = "approved"
            reply.reviewed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(reply)
            
            raise Exception(f"Failed to send reply: {str(e)}")
    
    async def edit_reply(
        self,
        reply_id: UUID,
        user_id: UUID,
        new_content: str
    ) -> SmartReplySchema:
        """
        Edit a smart reply draft
        
        Args:
            reply_id: Reply ID
            user_id: User ID
            new_content: Updated draft content
        
        Returns:
            Updated smart reply
        
        Validates: Requirements 8.4
        """
        reply = self.db.query(SmartReply).filter(
            SmartReply.id == reply_id,
            SmartReply.user_id == user_id,
            SmartReply.status == "pending"
        ).first()
        
        if not reply:
            raise ValueError("Reply not found or not pending")
        
        reply.draft_content = new_content
        reply.reviewed_at = datetime.utcnow()
        # Keep status as pending for re-approval
        
        self.db.commit()
        self.db.refresh(reply)
        
        return SmartReplySchema.model_validate(reply)
    
    async def reject_reply(self, reply_id: UUID, user_id: UUID) -> SmartReplySchema:
        """
        Reject a smart reply
        
        Args:
            reply_id: Reply ID
            user_id: User ID
        
        Returns:
            Updated smart reply
        
        Validates: Requirements 8.5
        """
        reply = self.db.query(SmartReply).filter(
            SmartReply.id == reply_id,
            SmartReply.user_id == user_id,
            SmartReply.status == "pending"
        ).first()
        
        if not reply:
            raise ValueError("Reply not found or not pending")
        
        reply.status = "rejected"
        reply.reviewed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(reply)
        
        return SmartReplySchema.model_validate(reply)
    
    async def _send_reply(
        self,
        original_message: Message,
        reply_content: str,
        user_id: UUID
    ) -> None:
        """
        Send a reply via the appropriate platform
        
        Args:
            original_message: Original message being replied to
            reply_content: Reply content to send
            user_id: User ID
        
        Validates: Requirements 8.3
        """
        # Get platform connection
        connection = self.db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.platform == original_message.platform
        ).first()
        
        if not connection:
            raise ValueError(f"No {original_message.platform} connection found for user")
        
        # Get platform adapter
        adapter = get_platform_adapter(original_message.platform, self.db)
        
        # Prepare outgoing message
        from app.integrations.interfaces import OutgoingMessage
        
        subject = None
        if original_message.subject:
            # Add Re: prefix if not already present
            subject = original_message.subject
            if not subject.startswith("Re:"):
                subject = f"Re: {subject}"
        
        outgoing_message = OutgoingMessage(
            recipient=original_message.sender,
            content=reply_content,
            subject=subject,
            thread_id=original_message.thread_id,
            metadata={
                "reply_to_message_id": original_message.platform_message_id
            }
        )
        
        # Send via platform adapter
        result = await adapter.send_message(
            str(user_id),
            connection.access_token,
            connection.refresh_token,
            outgoing_message
        )
        
        if not result.get("success"):
            raise Exception(f"Platform send failed: {result.get('error', 'Unknown error')}")
    
    async def record_interaction(
        self,
        user_id: str,
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ) -> None:
        """
        Record a user interaction for persona learning
        
        Args:
            user_id: User ID
            interaction_type: Type of interaction
            interaction_data: Interaction details
        
        Validates: Requirements 6.1
        """
        # Store observation in persona memory
        await self.persona_store.store_observation(
            user_id=user_id,
            observation_type=interaction_type,
            observation_data=interaction_data
        )


def get_reply_service(db: Session, store: Optional[InMemoryStore] = None) -> SmartReplyService:
    """
    Get a smart reply service instance
    
    Args:
        db: Database session
        store: Optional LangGraph Store
    
    Returns:
        SmartReplyService: Configured service
    """
    return SmartReplyService(db=db, store=store)
