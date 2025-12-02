"""
Error handling and notification system
Validates: Requirements 16.2
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories"""
    PLATFORM_API = "platform_api"
    AI_PIPELINE = "ai_pipeline"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    NETWORK = "network"
    UNKNOWN = "unknown"


class ErrorNotification:
    """
    Error notification data structure
    """
    def __init__(
        self,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.error = error
        self.category = category
        self.severity = severity
        self.user_id = user_id
        self.context = context or {}
        self.user_message = user_message or self._generate_user_message()
        self.timestamp = datetime.utcnow()
        self.error_type = type(error).__name__
        self.error_message = str(error)
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message"""
        if self.category == ErrorCategory.PLATFORM_API:
            return "We're having trouble connecting to one of your platforms. Please try again later."
        elif self.category == ErrorCategory.AI_PIPELINE:
            return "Our AI analysis is temporarily unavailable. Your messages are still being saved."
        elif self.category == ErrorCategory.DATABASE:
            return "We're experiencing technical difficulties. Please try again in a few moments."
        elif self.category == ErrorCategory.AUTHENTICATION:
            return "There was a problem with your authentication. Please log in again."
        elif self.category == ErrorCategory.NETWORK:
            return "Network connection issue. Please check your internet connection."
        else:
            return "An unexpected error occurred. Our team has been notified."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "error_type": self.error_type,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.user_message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }
    
    def log(self) -> None:
        """Log the error with appropriate level"""
        log_message = (
            f"[{self.category.value.upper()}] {self.error_type}: {self.error_message}"
        )
        
        if self.user_id:
            log_message = f"User {self.user_id} - {log_message}"
        
        if self.context:
            log_message = f"{log_message} | Context: {self.context}"
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=self.error)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=self.error)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)


class ErrorNotificationService:
    """
    Service for handling error notifications
    Validates: Requirements 16.2
    """
    
    def __init__(self):
        self.notifications = []  # In-memory storage for demo; use database in production
    
    def notify(
        self,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ) -> ErrorNotification:
        """
        Create and log an error notification
        
        Args:
            error: The exception that occurred
            category: Error category
            severity: Error severity
            user_id: Optional user ID
            context: Optional context information
            user_message: Optional custom user message
        
        Returns:
            ErrorNotification: The created notification
        """
        notification = ErrorNotification(
            error=error,
            category=category,
            severity=severity,
            user_id=user_id,
            context=context,
            user_message=user_message
        )
        
        # Log the error
        notification.log()
        
        # Store notification (in production, store in database)
        self.notifications.append(notification)
        
        # In production, you might also:
        # - Send email to user
        # - Send to monitoring service (Sentry, DataDog, etc.)
        # - Trigger alerts for critical errors
        # - Store in database for user to view later
        
        return notification
    
    def get_user_notifications(
        self,
        user_id: str,
        limit: int = 10
    ) -> list[ErrorNotification]:
        """
        Get recent error notifications for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications
        
        Returns:
            List of error notifications
        """
        user_notifications = [
            n for n in self.notifications
            if n.user_id == user_id
        ]
        
        # Sort by timestamp descending
        user_notifications.sort(key=lambda n: n.timestamp, reverse=True)
        
        return user_notifications[:limit]
    
    def clear_user_notifications(self, user_id: str) -> int:
        """
        Clear notifications for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Number of notifications cleared
        """
        count = len([n for n in self.notifications if n.user_id == user_id])
        self.notifications = [
            n for n in self.notifications
            if n.user_id != user_id
        ]
        return count


# Global error notification service instance
_error_service = ErrorNotificationService()


def get_error_service() -> ErrorNotificationService:
    """Get the global error notification service"""
    return _error_service


def notify_error(
    error: Exception,
    category: ErrorCategory,
    severity: ErrorSeverity,
    user_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    user_message: Optional[str] = None
) -> ErrorNotification:
    """
    Convenience function to notify an error
    
    Args:
        error: The exception that occurred
        category: Error category
        severity: Error severity
        user_id: Optional user ID
        context: Optional context information
        user_message: Optional custom user message
    
    Returns:
        ErrorNotification: The created notification
    """
    return _error_service.notify(
        error=error,
        category=category,
        severity=severity,
        user_id=user_id,
        context=context,
        user_message=user_message
    )
