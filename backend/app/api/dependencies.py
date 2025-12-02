"""
API dependencies for authentication and authorization
"""
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user as get_user_from_token, security
from app.models.user import User


async def require_authentication(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency that requires valid authentication
    
    Verifies JWT token via Auth0
    
    Returns:
        Dict containing user_id, email, and username
    
    Raises:
        HTTPException: If authentication fails
    """
    # Verify token and extract user info (Auth0 handles session validity)
    user_info = await get_user_from_token(credentials)
    return user_info


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(require_authentication),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that returns the current active user from database
    
    Args:
        current_user: User info from token (contains auth0_id)
        db: Database session
    
    Returns:
        User model instance
    
    Raises:
        HTTPException: If user not found in database
    """
    # Query by auth0_id, not by UUID id
    user = db.query(User).filter(User.auth0_id == current_user["auth0_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database"
        )
    
    return user


# Aliases for backward compatibility
require_auth = require_authentication
get_current_user = get_current_active_user
