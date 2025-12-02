"""
Platform connection service for managing platform integrations
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.platform import PlatformConnection
from app.models.user import User
from app.integrations.interfaces import PlatformInterface
from app.integrations.google.gmail import GoogleGmailAdapter
from app.integrations.google.calendar_adapter import GoogleCalendarAdapter
from app.integrations.slack.slack_adapter import SlackAdapter
from app.utils.retry import retry_with_exponential_backoff, PlatformAPIError
from app.utils.errors import notify_error, ErrorCategory, ErrorSeverity


class PlatformService:
    """Service for managing platform connections"""
    
    def __init__(self, db: Session, google_client_id: Optional[str] = None, 
                 google_client_secret: Optional[str] = None, google_redirect_uri: Optional[str] = None,
                 google_calendar_redirect_uri: Optional[str] = None,
                 slack_client_id: Optional[str] = None, slack_client_secret: Optional[str] = None,
                 slack_redirect_uri: Optional[str] = None):
        self.db = db
        
        # Initialize platform adapters
        self._adapters: Dict[str, PlatformInterface] = {}
        
        # Gmail adapter
        if google_client_id and google_client_secret:
            self._adapters["gmail"] = GoogleGmailAdapter(
                google_client_id, 
                google_client_secret,
                google_redirect_uri
            )
        
        # Calendar adapter (uses same Google credentials but different redirect URI)
        if google_client_id and google_client_secret:
            self._adapters["calendar"] = GoogleCalendarAdapter(
                google_client_id,
                google_client_secret,
                google_calendar_redirect_uri or google_redirect_uri
            )
        
        # Slack adapter
        if slack_client_id and slack_client_secret:
            self._adapters["slack"] = SlackAdapter(
                slack_client_id,
                slack_client_secret,
                slack_redirect_uri
            )
    
    def _get_adapter(self, platform: str) -> PlatformInterface:
        """
        Get the platform adapter for a given platform
        
        Args:
            platform: Platform name ('gmail', 'slack', 'calendar')
        
        Returns:
            PlatformInterface adapter
        
        Raises:
            HTTPException: If platform is not supported
        """
        adapter = self._adapters.get(platform)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        return adapter
    

    async def disconnect_platform(self, user_id: str, platform: str) -> Dict:
        """
        Disconnect a platform for a user
        
        Args:
            user_id: User ID
            platform: Platform name
        
        Returns:
            Dict with disconnection status
        
        Raises:
            HTTPException: If disconnection fails
        """
        # Get existing connection
        connection = self.db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.platform == platform
        ).first()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{platform.capitalize()} is not connected for this user"
            )
        
        try:
            # Get platform adapter
            adapter = self._get_adapter(platform)
            
            # Disconnect through adapter
            await adapter.disconnect(user_id)
            
            # Remove connection from database
            self.db.delete(connection)
            self.db.commit()
            
            return {
                "platform": platform,
                "status": "disconnected",
                "message": f"{platform.capitalize()} disconnected successfully"
            }
        except Exception as e:
            self.db.rollback()
            
            # Notify error
            notify_error(
                error=e,
                category=ErrorCategory.PLATFORM_API,
                severity=ErrorSeverity.MEDIUM,
                user_id=user_id,
                context={"platform": platform, "action": "disconnect"}
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to disconnect {platform}: {str(e)}"
            )
    
    def get_platform_status(self, user_id: str) -> Dict[str, bool]:
        """
        Get connection status for all platforms
        
        Args:
            user_id: User ID
        
        Returns:
            Dict mapping platform names to connection status
        """
        connections = self.db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id
        ).all()
        
        connected_platforms = {conn.platform for conn in connections}
        
        return {
            "gmail": "gmail" in connected_platforms,
            "slack": "slack" in connected_platforms,
            "calendar": "calendar" in connected_platforms,
        }
    
    def get_platform_connection(self, user_id: str, platform: str) -> Optional[PlatformConnection]:
        """
        Get platform connection for a user
        
        Args:
            user_id: User ID
            platform: Platform name
        
        Returns:
            PlatformConnection or None
        """
        return self.db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.platform == platform
        ).first()
    
    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        exceptions=(PlatformAPIError, ConnectionError, TimeoutError)
    )
    async def refresh_platform_token(self, user_id: str, platform: str) -> None:
        """
        Refresh access token for a platform
        
        Args:
            user_id: User ID
            platform: Platform name
        
        Raises:
            HTTPException: If refresh fails
        
        Validates: Requirements 16.1
        """
        connection = self.get_platform_connection(user_id, platform)
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{platform.capitalize()} is not connected"
            )
        
        if not connection.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token available"
            )
        
        try:
            # Get platform adapter
            adapter = self._get_adapter(platform)
            
            # Refresh token through adapter
            new_connection = await adapter.refresh_token(user_id, connection.refresh_token)
            
            # Update connection in database
            connection.access_token = new_connection.access_token
            if new_connection.refresh_token:
                connection.refresh_token = new_connection.refresh_token
            if new_connection.token_expires_at:
                connection.token_expires_at = new_connection.token_expires_at
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            
            # Notify error
            notify_error(
                error=e,
                category=ErrorCategory.PLATFORM_API,
                severity=ErrorSeverity.HIGH,
                user_id=user_id,
                context={"platform": platform, "action": "refresh_token"}
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to refresh token: {str(e)}"
            )
