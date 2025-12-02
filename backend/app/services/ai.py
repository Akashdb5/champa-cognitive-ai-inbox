"""
AI Service
Orchestrates AI Pipeline for message analysis, embedding generation, and storage.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.schemas.message import NormalizedMessage, MessageAnalysis as MessageAnalysisSchema
from app.models.message import MessageAnalysis as MessageAnalysisModel, ActionableItem
from app.ai.agents.analyzer import MessageAnalysisAgent, MessageAnalysisResult
from app.ai.embeddings.qdrant_client import get_qdrant_manager
from app.ai.fallback import get_basic_processor
from app.utils.errors import notify_error, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class AIService:
    """
    Service for AI-powered message analysis and vector storage.
    Implements the AI Pipeline orchestration from the design document.
    """
    
    def __init__(self, db: Session):
        """
        Initialize AI service
        
        Args:
            db: Database session
        """
        self.db = db
        self.analyzer = MessageAnalysisAgent()
        self.qdrant = get_qdrant_manager()
    
    async def analyze_message(self, message: NormalizedMessage) -> MessageAnalysisSchema:
        """
        Analyze a message using the AI Pipeline and store results
        
        This method:
        1. Runs message through analysis agent (summary, intent, priority, tasks, deadlines)
        2. Stores analysis results in PostgreSQL
        3. Generates and stores embeddings in Qdrant
        4. Links embeddings to message IDs
        5. Falls back to basic processing if AI Pipeline fails
        
        Args:
            message: Normalized message to analyze
        
        Returns:
            MessageAnalysisSchema: Analysis results
        
        Validates: Requirements 5.1, 13.1, 13.2, 13.3, 16.3
        """
        # Try AI analysis first
        try:
            analysis_result = await self.analyzer.analyze(message)
        except Exception as e:
            # Log error and notify
            logger.warning(f"AI Pipeline failed for message {message.id}, using fallback: {e}")
            notify_error(
                error=e,
                category=ErrorCategory.AI_PIPELINE,
                severity=ErrorSeverity.MEDIUM,
                user_id=message.user_id,
                context={"message_id": message.id, "platform": message.platform}
            )
            
            # Use fallback processor
            basic_processor = get_basic_processor()
            fallback_result = basic_processor.analyze(message)
            
            # Convert fallback result to analysis result format
            class FallbackResult:
                def __init__(self, data):
                    self.summary = data["summary"]
                    self.intent = data["intent"]
                    self.priority_score = data["priority_score"]
                    self.tasks = [type('Task', (), task) for task in data["tasks"]]
                    self.deadlines = [type('Deadline', (), dl) for dl in data["deadlines"]]
                    
                    # Add to_dict methods
                    for task in self.tasks:
                        task.to_dict = lambda self=task: {
                            "type": getattr(self, "type", "task"),
                            "description": getattr(self, "description", ""),
                            "deadline": getattr(self, "deadline", None)
                        }
                    
                    for dl in self.deadlines:
                        dl.to_dict = lambda self=dl: {
                            "description": getattr(self, "description", ""),
                            "date": getattr(self, "date", None)
                        }
            
            analysis_result = FallbackResult(fallback_result)
        
        # Store analysis in database
        db_analysis = MessageAnalysisModel(
            message_id=message.id,
            summary=analysis_result.summary,
            intent=analysis_result.intent,
            priority_score=analysis_result.priority_score,
            is_spam=getattr(analysis_result, 'is_spam', False),
            spam_score=getattr(analysis_result, 'spam_score', 0.0),
            spam_type=getattr(analysis_result, 'spam_type', 'none'),
            unsubscribe_link=getattr(analysis_result, 'unsubscribe_link', None)
        )
        self.db.add(db_analysis)
        
        # Store actionable items
        for task in analysis_result.tasks:
            actionable = ActionableItem(
                message_id=message.id,
                user_id=message.user_id,
                type=task.type,
                description=task.description,
                deadline=None,  # Will be set if deadline is parsed
                completed=False
            )
            self.db.add(actionable)
        
        for deadline in analysis_result.deadlines:
            # Try to parse deadline date if provided
            deadline_date = None
            if deadline.date:
                try:
                    # Simple date parsing - in production, use dateutil or similar
                    deadline_date = datetime.fromisoformat(deadline.date)
                except:
                    pass
            
            actionable = ActionableItem(
                message_id=message.id,
                user_id=message.user_id,
                type="deadline",
                description=deadline.description,
                deadline=deadline_date,
                completed=False
            )
            self.db.add(actionable)
        
        # Commit to database
        self.db.commit()
        self.db.refresh(db_analysis)
        
        # Generate smart reply suggestions if not spam, has reasonable priority, and sender is replyable
        should_generate_replies = (
            not getattr(analysis_result, 'is_spam', False) 
            and analysis_result.priority_score > 0.3
            and self._is_replyable_sender(message.sender)
        )
        
        if should_generate_replies:
            try:
                await self._generate_reply_suggestions(message)
            except Exception as e:
                # Don't fail analysis if smart reply generation fails
                logger.warning(f"Smart reply suggestion generation failed for message {message.id}: {e}")
        
        # Generate and store embedding in Qdrant
        try:
            await self.qdrant.store_message_embedding(
                message_id=message.id,
                user_id=message.user_id,
                platform=message.platform,
                content=message.content,
                timestamp=message.timestamp,
                subject=message.subject
            )
        except Exception as e:
            # Log error but don't fail the analysis
            print(f"Error storing embedding in Qdrant: {e}")
        
        # Return analysis schema
        return MessageAnalysisSchema(
            message_id=message.id,
            summary=analysis_result.summary,
            intent=analysis_result.intent,
            priority_score=analysis_result.priority_score,
            is_spam=getattr(analysis_result, 'is_spam', False),
            spam_score=getattr(analysis_result, 'spam_score', 0.0),
            spam_type=getattr(analysis_result, 'spam_type', 'none'),
            unsubscribe_link=getattr(analysis_result, 'unsubscribe_link', None),
            tasks=[task.to_dict() for task in analysis_result.tasks],
            deadlines=[deadline.to_dict() for deadline in analysis_result.deadlines]
        )
    
    async def semantic_search(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search over user's messages
        
        Args:
            user_id: User ID to search messages for
            query: Search query text
            limit: Maximum number of results
        
        Returns:
            List[Dict[str, Any]]: Search results with message metadata
        
        Validates: Requirements 13.4, 13.5
        """
        # Search in Qdrant
        results = await self.qdrant.semantic_search(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        return results
    
    async def get_message_analysis(self, message_id: str) -> Optional[MessageAnalysisSchema]:
        """
        Get stored analysis for a message
        
        Args:
            message_id: Message ID
        
        Returns:
            Optional[MessageAnalysisSchema]: Analysis if found
        """
        analysis = self.db.query(MessageAnalysisModel).filter(
            MessageAnalysisModel.message_id == message_id
        ).first()
        
        if not analysis:
            return None
        
        # Get actionable items
        actionables = self.db.query(ActionableItem).filter(
            ActionableItem.message_id == message_id
        ).all()
        
        tasks = []
        deadlines = []
        
        for item in actionables:
            if item.type in ["task", "meeting"]:
                tasks.append({
                    "type": item.type,
                    "description": item.description,
                    "deadline": item.deadline.isoformat() if item.deadline else None
                })
            elif item.type == "deadline":
                deadlines.append({
                    "description": item.description,
                    "date": item.deadline.isoformat() if item.deadline else None
                })
        
        return MessageAnalysisSchema(
            message_id=analysis.message_id,
            summary=analysis.summary,
            intent=analysis.intent,
            priority_score=analysis.priority_score,
            tasks=tasks,
            deadlines=deadlines
        )
    
    async def reanalyze_message(self, message: NormalizedMessage) -> MessageAnalysisSchema:
        """
        Re-analyze a message (useful if analysis failed or needs updating)
        
        Args:
            message: Normalized message to re-analyze
        
        Returns:
            MessageAnalysisSchema: Updated analysis results
        """
        # Delete existing analysis
        self.db.query(MessageAnalysisModel).filter(
            MessageAnalysisModel.message_id == message.id
        ).delete()
        
        # Delete existing actionable items
        self.db.query(ActionableItem).filter(
            ActionableItem.message_id == message.id
        ).delete()
        
        self.db.commit()
        
        # Run new analysis
        return await self.analyze_message(message)
    
    async def delete_message_data(self, message_id: str) -> bool:
        """
        Delete all AI-related data for a message
        
        Args:
            message_id: Message ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Delete from PostgreSQL
            self.db.query(MessageAnalysisModel).filter(
                MessageAnalysisModel.message_id == message_id
            ).delete()
            
            self.db.query(ActionableItem).filter(
                ActionableItem.message_id == message_id
            ).delete()
            
            self.db.commit()
            
            # Delete from Qdrant
            await self.qdrant.delete_message_embedding(message_id)
            
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting message data: {e}")
            return False
    
    async def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all AI-related data for a user
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Delete actionable items
            self.db.query(ActionableItem).filter(
                ActionableItem.user_id == user_id
            ).delete()
            
            self.db.commit()
            
            # Delete embeddings from Qdrant
            await self.qdrant.delete_user_embeddings(user_id)
            
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting user data: {e}")
            return False
    
    def get_user_actionables(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        limit: int = 100
    ) -> List[ActionableItem]:
        """
        Get actionable items for a user
        
        Args:
            user_id: User ID
            completed: Filter by completion status (None = all)
            limit: Maximum number of items
        
        Returns:
            List[ActionableItem]: Actionable items
        """
        query = self.db.query(ActionableItem).filter(
            ActionableItem.user_id == user_id
        )
        
        if completed is not None:
            query = query.filter(ActionableItem.completed == completed)
        
        query = query.order_by(ActionableItem.deadline.asc().nullslast())
        query = query.limit(limit)
        
        return query.all()
    
    def mark_actionable_complete(self, actionable_id: str) -> bool:
        """
        Mark an actionable item as complete
        
        Args:
            actionable_id: Actionable item ID
        
        Returns:
            bool: True if successful
        """
        try:
            actionable = self.db.query(ActionableItem).filter(
                ActionableItem.id == actionable_id
            ).first()
            
            if actionable:
                actionable.completed = True
                self.db.commit()
                return True
            
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error marking actionable complete: {e}")
            return False
    
    def _is_replyable_sender(self, sender: str) -> bool:
        """
        Check if a sender email address is replyable (not a no-reply address)
        
        Args:
            sender: Email sender address
        
        Returns:
            bool: True if sender can receive replies, False otherwise
        """
        if not sender:
            return False
        
        # Convert to lowercase for case-insensitive matching
        sender_lower = sender.lower()
        
        # Common no-reply patterns
        no_reply_patterns = [
            'no-reply',
            'noreply',
            'no_reply',
            'donotreply',
            'do-not-reply',
            'do_not_reply',
            'notifications',
            'automated',
            'mailer-daemon',
            'postmaster'
        ]
        
        # Check if sender contains any no-reply pattern
        for pattern in no_reply_patterns:
            if pattern in sender_lower:
                logger.info(f"Skipping reply generation for no-reply sender: {sender}")
                return False
        
        return True
    
    async def _generate_reply_suggestions(self, message: NormalizedMessage) -> None:
        """
        Generate quick reply suggestions for a message (stored in smart_replies table)
        
        This is different from the deep agent smart reply generation - these are
        quick suggestions shown during message analysis.
        
        Args:
            message: Message to generate suggestions for
        """
        try:
            from app.ai.chains.smart_reply import generate_smart_replies
            from app.models.message import SmartReply as SmartReplyModel
            
            # Generate reply suggestions using AI
            suggestions = await generate_smart_replies(
                platform=message.platform,
                sender=message.sender,
                subject=message.subject or "",
                content=message.content
            )
            
            # Store suggestions in database
            for suggestion in suggestions:
                db_reply = SmartReplyModel(
                    message_id=message.id,
                    user_id=message.user_id,
                    draft_content=suggestion["text"],
                    status="suggestion"  # Mark as suggestion, not pending approval
                )
                self.db.add(db_reply)
            
            self.db.commit()
            
        except Exception as e:
            logger.warning(f"Failed to generate reply suggestions: {e}")
            # Don't fail the analysis if suggestions fail
