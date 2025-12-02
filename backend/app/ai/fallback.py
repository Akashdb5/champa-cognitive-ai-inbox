"""
Basic text processing fallback for AI Pipeline failures
Validates: Requirements 16.3
"""
import re
from typing import List, Optional
from datetime import datetime

from app.schemas.message import NormalizedMessage


class BasicTextProcessor:
    """
    Basic text processing fallback when AI Pipeline is unavailable
    Provides simple rule-based analysis without LLM
    """
    
    def __init__(self):
        # Common task keywords
        self.task_keywords = [
            "todo", "task", "action item", "need to", "should", "must",
            "please", "can you", "could you", "would you"
        ]
        
        # Common deadline keywords
        self.deadline_keywords = [
            "deadline", "due", "by", "before", "until", "eod", "eow",
            "today", "tomorrow", "next week", "this week"
        ]
        
        # Priority keywords
        self.high_priority_keywords = [
            "urgent", "asap", "critical", "important", "emergency",
            "immediately", "high priority"
        ]
        
        self.medium_priority_keywords = [
            "soon", "when possible", "at your convenience"
        ]
    
    def generate_summary(self, message: NormalizedMessage) -> str:
        """
        Generate a basic summary by truncating content
        
        Args:
            message: Normalized message
        
        Returns:
            str: Summary (first 150 characters)
        """
        content = message.content.strip()
        
        # Use subject if available
        if message.subject:
            return message.subject[:150]
        
        # Otherwise truncate content
        if len(content) <= 150:
            return content
        
        return content[:147] + "..."
    
    def classify_intent(self, message: NormalizedMessage) -> str:
        """
        Classify message intent using simple keyword matching
        
        Args:
            message: Normalized message
        
        Returns:
            str: Intent classification
        """
        content_lower = message.content.lower()
        
        # Check for questions
        if "?" in message.content:
            return "question"
        
        # Check for tasks
        if any(keyword in content_lower for keyword in self.task_keywords):
            return "task_request"
        
        # Check for meeting/calendar
        if message.platform == "calendar":
            return "meeting"
        
        # Check for information sharing
        if any(word in content_lower for word in ["fyi", "info", "update", "announcement"]):
            return "information"
        
        return "general"
    
    def extract_tasks(self, message: NormalizedMessage) -> List[dict]:
        """
        Extract potential tasks using keyword matching
        
        Args:
            message: Normalized message
        
        Returns:
            List[dict]: Extracted tasks
        """
        tasks = []
        content_lower = message.content.lower()
        
        # Look for task indicators
        for keyword in self.task_keywords:
            if keyword in content_lower:
                # Extract sentence containing the keyword
                sentences = re.split(r'[.!?\n]', message.content)
                for sentence in sentences:
                    if keyword in sentence.lower() and len(sentence.strip()) > 10:
                        tasks.append({
                            "type": "task",
                            "description": sentence.strip()[:200],
                            "deadline": None
                        })
                        break  # Only one task per keyword
        
        # Limit to 3 tasks
        return tasks[:3]
    
    def detect_deadlines(self, message: NormalizedMessage) -> List[dict]:
        """
        Detect potential deadlines using keyword matching
        
        Args:
            message: Normalized message
        
        Returns:
            List[dict]: Detected deadlines
        """
        deadlines = []
        content_lower = message.content.lower()
        
        # Look for deadline indicators
        for keyword in self.deadline_keywords:
            if keyword in content_lower:
                # Extract sentence containing the keyword
                sentences = re.split(r'[.!?\n]', message.content)
                for sentence in sentences:
                    if keyword in sentence.lower() and len(sentence.strip()) > 10:
                        deadlines.append({
                            "description": sentence.strip()[:200],
                            "date": None  # Cannot parse dates without AI
                        })
                        break
        
        # Limit to 2 deadlines
        return deadlines[:2]
    
    def calculate_priority(self, message: NormalizedMessage) -> float:
        """
        Calculate priority score using keyword matching
        
        Args:
            message: Normalized message
        
        Returns:
            float: Priority score (0.0 to 1.0)
        """
        content_lower = message.content.lower()
        
        # Check for high priority keywords
        if any(keyword in content_lower for keyword in self.high_priority_keywords):
            return 0.9
        
        # Check for medium priority keywords
        if any(keyword in content_lower for keyword in self.medium_priority_keywords):
            return 0.6
        
        # Check for questions (medium priority)
        if "?" in message.content:
            return 0.5
        
        # Check for tasks
        if any(keyword in content_lower for keyword in self.task_keywords):
            return 0.5
        
        # Default low priority
        return 0.3
    
    def analyze(self, message: NormalizedMessage) -> dict:
        """
        Perform basic analysis on a message
        
        Args:
            message: Normalized message
        
        Returns:
            dict: Analysis results
        """
        return {
            "summary": self.generate_summary(message),
            "intent": self.classify_intent(message),
            "priority_score": self.calculate_priority(message),
            "tasks": self.extract_tasks(message),
            "deadlines": self.detect_deadlines(message),
            "fallback_used": True  # Flag to indicate fallback was used
        }


# Global instance
_basic_processor = BasicTextProcessor()


def get_basic_processor() -> BasicTextProcessor:
    """Get the global basic text processor instance"""
    return _basic_processor
