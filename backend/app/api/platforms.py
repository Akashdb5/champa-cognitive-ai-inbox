"""
Platform connection API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.platform import PlatformService
from app.schemas.platform import (
    PlatformConnectionResponse,
    PlatformStatus
)
from app.core.config import settings
from app.utils.token_refresh import create_token_refresh_middleware

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


def get_platform_service(db: Session = Depends(get_db)) -> PlatformService:
    """Dependency to get platform service"""
    return PlatformService(
        db,
        google_client_id=settings.GOOGLE_CLIENT_ID,
        google_client_secret=settings.GOOGLE_CLIENT_SECRET,
        google_redirect_uri=settings.GOOGLE_REDIRECT_URI,
        google_calendar_redirect_uri=settings.GOOGLE_CALENDAR_REDIRECT_URI,
        slack_client_id=settings.SLACK_CLIENT_ID,
        slack_client_secret=settings.SLACK_CLIENT_SECRET,
        slack_redirect_uri=settings.SLACK_REDIRECT_URI
    )


@router.get("/", response_model=PlatformStatus)
async def get_platform_status(
    current_user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service)
):
    """
    Get connection status for all platforms
    
    Returns the connection status (connected/disconnected) for Gmail, Slack, and Calendar.
    """
    status_dict = platform_service.get_platform_status(str(current_user.id))
    return PlatformStatus(**status_dict)


@router.get("/{platform}/auth-url", response_model=PlatformConnectionResponse)
async def get_auth_url(
    platform: str,
    current_user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service)
):
    """
    Get OAuth authorization URL for platform connection
    
    Returns the URL where the user should be redirected to authorize the connection.
    
    Args:
        platform: Platform name ('gmail', 'slack')
    
    Returns:
        Connection response with redirect URL for user authorization
    """
    if platform not in ["gmail", "slack", "calendar"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform. Supported platforms: 'gmail', 'slack', 'calendar'"
        )
    
    # Generate state for CSRF protection with user_id embedded
    import secrets
    import logging
    logger = logging.getLogger(__name__)
    
    # State format: userid_randomstring (so we can extract user_id in callback)
    random_part = secrets.token_urlsafe(32)
    state = f"{current_user.id}_{random_part}"
    
    adapter = platform_service._adapters.get(platform)
    if not adapter:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{platform.capitalize()} not configured. Please set {platform.upper()}_CLIENT_ID and {platform.upper()}_CLIENT_SECRET"
        )
    
    # Get the appropriate redirect URI
    if platform == "gmail":
        redirect_uri = settings.GOOGLE_REDIRECT_URI
    elif platform == "calendar":
        redirect_uri = settings.GOOGLE_CALENDAR_REDIRECT_URI
    else:
        redirect_uri = settings.SLACK_REDIRECT_URI
    logger.info(f"{platform.capitalize()} OAuth redirect URI: {redirect_uri}")
    
    # Generate authorization URL
    auth_url = adapter.get_authorization_url(
        redirect_uri=redirect_uri,
        state=state
    )
    
    logger.info(f"Generated {platform} auth URL for user {current_user.id}")
    
    return PlatformConnectionResponse(
        platform=platform,
        status="pending",
        message=f"Please authorize {platform} connection",
        redirect_url=auth_url,
        connection_request_id=state
    )


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    OAuth callback endpoint
    
    Handles the OAuth callback after user authorizes the connection.
    This endpoint is called by the OAuth provider (Gmail, Slack) after user authorization.
    It exchanges the code for tokens, stores them, and redirects to the frontend.
    
    Args:
        platform: Platform name ('gmail', 'slack')
        code: Authorization code from OAuth provider
        state: State parameter (contains user_id for authentication)
    
    Returns:
        Redirect to frontend OAuth success/error page
    """
    from fastapi.responses import RedirectResponse
    
    if platform not in ["gmail", "slack", "calendar"]:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/oauth-redirect?error=invalid_platform",
            status_code=302
        )
    
    try:
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"OAuth callback for {platform}")
        logger.info(f"Code: {code[:20]}...")
        logger.info(f"State: {state}")
        
        # Extract user_id from state (state format: "userid_randomstring")
        # For now, we'll need to decode the state to get user_id
        # TODO: Store state in database/cache with user_id mapping
        user_id = state.split('_')[0] if '_' in state else state
        logger.info(f"Extracted user_id from state: {user_id}")
        
        # Get platform service
        platform_service = PlatformService(
            db,
            google_client_id=settings.GOOGLE_CLIENT_ID,
            google_client_secret=settings.GOOGLE_CLIENT_SECRET,
            google_redirect_uri=settings.GOOGLE_REDIRECT_URI,
            google_calendar_redirect_uri=settings.GOOGLE_CALENDAR_REDIRECT_URI,
            slack_client_id=settings.SLACK_CLIENT_ID,
            slack_client_secret=settings.SLACK_CLIENT_SECRET,
            slack_redirect_uri=settings.SLACK_REDIRECT_URI
        )
        
        # Get adapter
        adapter = platform_service._adapters.get(platform)
        if not adapter:
            logger.error(f"{platform} adapter not configured")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/oauth-redirect?error={platform}_not_configured",
                status_code=302
            )
        
        # Exchange code for tokens
        logger.info(f"Exchanging code for tokens...")
        connection = await adapter.connect(user_id, code)
        logger.info(f"Got connection with access_token: {connection.access_token[:20]}...")
        
        # Store connection in database
        from app.models.platform import PlatformConnection
        
        # Check if connection already exists
        existing = db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.platform == platform
        ).first()
        
        if existing:
            # Update existing connection
            existing.access_token = connection.access_token
            existing.refresh_token = connection.refresh_token
            existing.token_expires_at = connection.token_expires_at
            logger.info(f"Updated existing {platform} connection for user {user_id}")
        else:
            # Create new connection
            db_connection = PlatformConnection(
                user_id=user_id,
                platform=platform,
                access_token=connection.access_token,
                refresh_token=connection.refresh_token,
                token_expires_at=connection.token_expires_at,
            )
            db.add(db_connection)
            logger.info(f"Created new {platform} connection for user {user_id}")
        
        db.commit()
        
        # Redirect to frontend success page
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/oauth-redirect?code={code}&state={state}&platform={platform}",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/oauth-redirect?error={str(e)}",
            status_code=302
        )


@router.delete("/{platform}/disconnect", response_model=PlatformConnectionResponse)
async def disconnect_platform(
    platform: str,
    current_user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service)
):
    """
    Disconnect a platform
    
    Removes the connection between the user's account and the specified platform.
    
    Args:
        platform: Platform name ('gmail', 'slack', 'calendar')
    
    Returns:
        Disconnection response with status
    """
    if platform not in ["gmail", "slack", "calendar"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform. Must be 'gmail', 'slack', or 'calendar'"
        )
    
    result = await platform_service.disconnect_platform(
        user_id=str(current_user.id),
        platform=platform
    )
    
    return PlatformConnectionResponse(
        platform=result["platform"],
        status="disconnected",
        message=result["message"]
    )


@router.post("/{platform}/refresh")
async def refresh_platform_token(
    platform: str,
    current_user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service),
    db: Session = Depends(get_db)
):
    """
    Refresh platform access token
    
    Refreshes the OAuth access token for the specified platform.
    This endpoint can be called manually or automatically when token expires.
    
    Args:
        platform: Platform name ('gmail', 'slack', 'calendar')
    
    Returns:
        Success message
    
    Validates: Requirements 16.5
    """
    if platform not in ["gmail", "slack", "calendar"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform. Must be 'gmail', 'slack', or 'calendar'"
        )
    
    await platform_service.refresh_platform_token(
        user_id=str(current_user.id),
        platform=platform
    )
    
    return {"message": f"{platform.capitalize()} token refreshed successfully"}


@router.get("/{platform}/token-status")
async def get_token_status(
    platform: str,
    current_user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service)
):
    """
    Check token expiration status for a platform
    
    Returns information about whether the token is expired or expiring soon.
    
    Args:
        platform: Platform name ('gmail', 'slack', 'calendar')
    
    Returns:
        Token status information
    
    Validates: Requirements 16.5
    """
    if platform not in ["gmail", "slack", "calendar"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform. Must be 'gmail', 'slack', or 'calendar'"
        )
    
    connection = platform_service.get_platform_connection(str(current_user.id), platform)
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{platform.capitalize()} is not connected"
        )
    
    # Create middleware to check token status
    middleware = create_token_refresh_middleware(platform_service)
    status_info = middleware.check_token_expiration(connection)
    
    if status_info:
        return status_info
    
    return {
        "status": "valid",
        "message": "Token is valid",
        "expires_at": connection.token_expires_at.isoformat() if connection.token_expires_at else None
    }
