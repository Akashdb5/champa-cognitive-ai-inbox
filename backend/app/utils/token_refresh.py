"""
OAuth token refresh utilities
Validates: Requirements 16.5
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.platform import PlatformConnection

logger = logging.getLogger(__name__)


def is_token_expired(connection: PlatformConnection, buffer_minutes: int = 5) -> bool:
    """
    Check if a token is expired or about to expire
    
    Args:
        connection: Platform connection to check
        buffer_minutes: Minutes before expiration to consider token expired
    
    Returns:
        bool: True if token is expired or about to expire
    
    Validates: Requirements 16.5
    """
    if not connection.token_expires_at:
        # If no expiration time, assume token is valid
        return False
    
    # Add buffer to avoid using token right before it expires
    expiration_with_buffer = connection.token_expires_at - timedelta(minutes=buffer_minutes)
    
    return datetime.utcnow() >= expiration_with_buffer


def needs_refresh(connection: PlatformConnection) -> bool:
    """
    Check if a token needs to be refreshed
    
    Args:
        connection: Platform connection to check
    
    Returns:
        bool: True if token needs refresh
    
    Validates: Requirements 16.5
    """
    # Check if token is expired
    if is_token_expired(connection):
        # Only refresh if we have a refresh token
        return connection.refresh_token is not None
    
    return False


class TokenRefreshError(Exception):
    """Exception raised when token refresh fails"""
    pass


class TokenRefreshMiddleware:
    """
    Middleware for automatic token refresh
    Validates: Requirements 16.5
    """
    
    def __init__(self, platform_service):
        """
        Initialize token refresh middleware
        
        Args:
            platform_service: PlatformService instance
        """
        self.platform_service = platform_service
    
    async def ensure_valid_token(
        self,
        user_id: str,
        platform: str,
        db: Session
    ) -> PlatformConnection:
        """
        Ensure platform connection has a valid token, refreshing if necessary
        
        Args:
            user_id: User ID
            platform: Platform name
            db: Database session
        
        Returns:
            PlatformConnection: Connection with valid token
        
        Raises:
            HTTPException: If token refresh fails or connection not found
        
        Validates: Requirements 16.5
        """
        # Get platform connection
        connection = self.platform_service.get_platform_connection(user_id, platform)
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{platform.capitalize()} is not connected. Please connect your account."
            )
        
        # Check if token needs refresh
        if needs_refresh(connection):
            logger.info(f"Token expired for user {user_id} on {platform}, attempting refresh")
            
            try:
                # Attempt to refresh token
                await self.platform_service.refresh_platform_token(user_id, platform)
                
                # Get updated connection
                db.refresh(connection)
                
                logger.info(f"Successfully refreshed token for user {user_id} on {platform}")
            
            except Exception as e:
                logger.error(f"Failed to refresh token for user {user_id} on {platform}: {e}")
                
                # Token refresh failed - user needs to re-authenticate
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=(
                        f"Your {platform.capitalize()} connection has expired. "
                        "Please reconnect your account."
                    )
                )
        
        return connection
    
    def check_token_expiration(
        self,
        connection: PlatformConnection
    ) -> Optional[dict]:
        """
        Check token expiration and return status
        
        Args:
            connection: Platform connection to check
        
        Returns:
            Optional[dict]: Status dict if token is expired, None otherwise
        
        Validates: Requirements 16.5
        """
        if is_token_expired(connection):
            if connection.refresh_token:
                return {
                    "status": "expired",
                    "message": "Token expired, refresh required",
                    "can_refresh": True
                }
            else:
                return {
                    "status": "expired",
                    "message": "Token expired, re-authentication required",
                    "can_refresh": False
                }
        
        # Check if token expires soon (within 1 hour)
        if connection.token_expires_at:
            time_until_expiry = connection.token_expires_at - datetime.utcnow()
            if time_until_expiry < timedelta(hours=1):
                return {
                    "status": "expiring_soon",
                    "message": f"Token expires in {time_until_expiry.seconds // 60} minutes",
                    "expires_at": connection.token_expires_at.isoformat()
                }
        
        return None


def create_token_refresh_middleware(platform_service):
    """
    Factory function to create token refresh middleware
    
    Args:
        platform_service: PlatformService instance
    
    Returns:
        TokenRefreshMiddleware: Configured middleware
    """
    return TokenRefreshMiddleware(platform_service)
