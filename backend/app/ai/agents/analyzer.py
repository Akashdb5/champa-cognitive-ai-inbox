"""
Message Analysis Agent
Orchestrates all analysis chains to process messages.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.schemas.message import NormalizedMessage
from app.ai.chains.summarize import summarize_message
from app.ai.chains.classify import classify_intent
from app.ai.chains.extract import extract_tasks, detect_deadlines
from app.ai.chains.prioritize import calculate_priority


class Task:
    """Represents an extracted task"""
    def __init__(self, task_type: str, description: str, deadline: Optional[str] = None):
        self.type = task_type
        self.description = description
        self.deadline = deadline
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "description": self.description,
            "deadline": self.deadline
        }


class Deadline:
    """Represents a detected deadline"""
    def __init__(self, description: str, date: Optional[str] = None):
        self.description = description
        self.date = date
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "date": self.date
        }


class MessageAnalysisResult:
    """Result of message analysis"""
    def __init__(
        self,
        summary: str,
        intent: str,
        priority_score: float,
        tasks: List[Task],
        deadlines: List[Deadline],
        is_spam: bool = False,
        spam_score: float = 0.0,
        spam_type: str = "none",
        unsubscribe_link: Optional[str] = None
    ):
        self.summary = summary
        self.intent = intent
        self.priority_score = priority_score
        self.tasks = tasks
        self.deadlines = deadlines
        self.is_spam = is_spam
        self.spam_score = spam_score
        self.spam_type = spam_type
        self.unsubscribe_link = unsubscribe_link
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "intent": self.intent,
            "priority_score": self.priority_score,
            "tasks": [task.to_dict() for task in self.tasks],
            "deadlines": [deadline.to_dict() for deadline in self.deadlines],
            "is_spam": self.is_spam,
            "spam_score": self.spam_score,
            "spam_type": self.spam_type,
            "unsubscribe_link": self.unsubscribe_link
        }


class MessageAnalysisAgent:
    """
    Agent that analyzes messages using multiple LangChain chains.
    Implements the message analysis workflow from the design document.
    """
    
    async def analyze(self, message: NormalizedMessage) -> MessageAnalysisResult:
        """
        Analyze a message using all analysis chains
        
        Args:
            message: Normalized message to analyze
        
        Returns:
            MessageAnalysisResult: Complete analysis results
        """
        # Extract message fields
        platform = message.platform
        sender = message.sender
        subject = message.subject or ""
        content = message.content
        metadata = message.metadata
        
        # Run all analysis chains in parallel for efficiency
        import asyncio
        from app.ai.chains.spam_detection import detect_spam
        
        results = await asyncio.gather(
            summarize_message(platform, sender, subject, content),
            classify_intent(platform, sender, subject, content),
            calculate_priority(platform, sender, subject, content),
            extract_tasks(platform, sender, subject, content),
            detect_deadlines(platform, sender, subject, content),
            detect_spam(platform, sender, subject, content, metadata),
            return_exceptions=True
        )
        
        # Unpack results with error handling
        summary = results[0] if not isinstance(results[0], Exception) else "Error generating summary"
        intent = results[1] if not isinstance(results[1], Exception) else "other"
        priority_score = results[2] if not isinstance(results[2], Exception) else 0.5
        task_tuples = results[3] if not isinstance(results[3], Exception) else []
        deadline_tuples = results[4] if not isinstance(results[4], Exception) else []
        spam_result = results[5] if not isinstance(results[5], Exception) else {
            "is_spam": False, "spam_score": 0.0, "spam_type": "none", "unsubscribe_link": None
        }
        
        # Convert tuples to objects
        tasks = [Task(task_type, description) for task_type, description in task_tuples]
        deadlines = [Deadline(description, date) for description, date in deadline_tuples]
        
        return MessageAnalysisResult(
            summary=summary,
            intent=intent,
            priority_score=priority_score,
            tasks=tasks,
            deadlines=deadlines,
            is_spam=spam_result["is_spam"],
            spam_score=spam_result["spam_score"],
            spam_type=spam_result["spam_type"],
            unsubscribe_link=spam_result.get("unsubscribe_link")
        )
    
    async def summarize(self, message: NormalizedMessage) -> str:
        """
        Generate a summary for a message
        
        Args:
            message: Normalized message to summarize
        
        Returns:
            str: Message summary
        """
        return await summarize_message(
            message.platform,
            message.sender,
            message.subject or "",
            message.content
        )
    
    async def classify_intent(self, message: NormalizedMessage) -> str:
        """
        Classify the intent of a message
        
        Args:
            message: Normalized message to classify
        
        Returns:
            str: Intent classification
        """
        return await classify_intent(
            message.platform,
            message.sender,
            message.subject or "",
            message.content
        )
    
    async def extract_tasks(self, message: NormalizedMessage) -> List[Task]:
        """
        Extract tasks from a message
        
        Args:
            message: Normalized message to extract tasks from
        
        Returns:
            List[Task]: Extracted tasks
        """
        task_tuples = await extract_tasks(
            message.platform,
            message.sender,
            message.subject or "",
            message.content
        )
        return [Task(task_type, description) for task_type, description in task_tuples]
    
    async def detect_deadlines(self, message: NormalizedMessage) -> List[Deadline]:
        """
        Detect deadlines in a message
        
        Args:
            message: Normalized message to detect deadlines in
        
        Returns:
            List[Deadline]: Detected deadlines
        """
        deadline_tuples = await detect_deadlines(
            message.platform,
            message.sender,
            message.subject or "",
            message.content
        )
        return [Deadline(description, date) for description, date in deadline_tuples]
    
    async def calculate_priority(self, message: NormalizedMessage) -> float:
        """
        Calculate priority score for a message
        
        Args:
            message: Normalized message to score
        
        Returns:
            float: Priority score between 0.0 and 1.0
        """
        return await calculate_priority(
            message.platform,
            message.sender,
            message.subject or "",
            message.content
        )
