"""
Abstract platform interfaces for platform integrations

This module defines the abstract base classes that all platform adapters must implement.
This allows for easy addition of new platforms with consistent interfaces.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class RawMessage(BaseModel):
    """Raw message data from a platform before normalization"""
    platform_message_id: str
    sender: str
    content: str
    timestamp: datetime
    subject: Optional[str] = None
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class OutgoingMessage(BaseModel):
    """Message to be sent to a platform"""
    recipient: str
    content: str
    subject: Optional[str] = None
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class MessageResult(BaseModel):
    """Result of sending a message"""
    success: bool
    platform_message_id: Optional[str] = None
    error: Optional[str] = None


class Connection(BaseModel):
    """Platform connection information"""
    platform: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    redirect_url: Optional[str] = None  # OAuth redirect URL for user authorization


class PlatformInterface(ABC):
    """
    Abstract base class for platform integrations
    
    All platform adapters must implement this interface.
    This ensures that the core system logic is decoupled from the specific
    integration provider.
    """
    
    @abstractmethod
    async def connect(self, user_id: str, auth_code: str) -> Connection:
        """
        Connect a user's account to the platform using OAuth authorization code
        
        Args:
            user_id: The user's ID in our system
            auth_code: OAuth authorization code from the platform
        
        Returns:
            Connection object with access tokens and metadata
        
        Raises:
            Exception: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self, user_id: str) -> None:
        """
        Disconnect a user's account from the platform
        
        Args:
            user_id: The user's ID in our system
        
        Raises:
            Exception: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def fetch_messages(self, user_id: str, access_token: str, refresh_token: str,
                            since: Optional[datetime] = None) -> List[RawMessage]:
        """
        Fetch messages from the platform for a user
        
        Args:
            user_id: The user's ID in our system
            access_token: User's access token
            refresh_token: User's refresh token
            since: Optional datetime to fetch messages after this time
        
        Returns:
            List of RawMessage objects
        
        Raises:
            Exception: If fetching fails
        """
        pass
    
    @abstractmethod
    async def send_message(self, user_id: str, access_token: str, refresh_token: str,
                          message: OutgoingMessage) -> MessageResult:
        """
        Send a message through the platform
        
        Args:
            user_id: The user's ID in our system
            access_token: User's access token
            refresh_token: User's refresh token
            message: The message to send
        
        Returns:
            MessageResult indicating success or failure
        
        Raises:
            Exception: If sending fails
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, user_id: str, refresh_token: str) -> Connection:
        """
        Refresh an expired access token
        
        Args:
            user_id: The user's ID in our system
            refresh_token: The refresh token
        
        Returns:
            Updated Connection object with new tokens
        
        Raises:
            Exception: If refresh fails
        """
        pass


def get_platform_adapter(platform: str, db) -> PlatformInterface:
    """
    Get the appropriate platform adapter for a given platform
    
    Args:
        platform: Platform name (gmail, slack, calendar)
        db: Database session
    
    Returns:
        PlatformInterface implementation for the platform
    
    Raises:
        ValueError: If platform is not supported
    """
    from app.integrations.google.gmail import GoogleGmailAdapter
    from app.integrations.slack.slack_adapter import SlackAdapter
    from app.integrations.google.calendar_adapter import GoogleCalendarAdapter
    
    adapters = {
        "gmail": GoogleGmailAdapter,
        "slack": SlackAdapter,
        "calendar": GoogleCalendarAdapter
    }
    
    adapter_class = adapters.get(platform)
    if not adapter_class:
        raise ValueError(f"Unsupported platform: {platform}")
    
    return adapter_class(db)
