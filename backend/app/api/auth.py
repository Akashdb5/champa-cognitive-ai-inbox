"""
Authentication API endpoints - Auth0 only
"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.auth import AuthService
from app.schemas.auth import AuthResponse
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/logout")
async def logout(
    refresh_token: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking their Auth0 refresh token
    """
    auth_service = AuthService(db)
    await auth_service.logout(refresh_token)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information from Auth0 token
    
    This endpoint also ensures the user exists in our database
    """
    auth_service = AuthService(db)
    
    # Get or create user in our database
    user = auth_service.get_or_create_user(
        auth0_id=current_user["auth0_id"],
        email=current_user["email"],
        username=current_user["username"]
    )
    
    return AuthResponse(
        user_id=str(user.id),
        email=user.email,
        username=user.username,
        access_token=""  # Token is already in the request header
    )


@router.get("/profile", response_model=UserSchema)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full user profile including additional fields
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_auth0_id(current_user["auth0_id"])
    
    if not user:
        # Get or create user if not found
        user = auth_service.get_or_create_user(
            auth0_id=current_user["auth0_id"],
            email=current_user["email"],
            username=current_user["username"]
        )
    
    return user


@router.patch("/profile", response_model=UserSchema)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile fields (phone, location, timezone, website)
    """
    auth_service = AuthService(db)
    user = auth_service.update_user_profile(
        auth0_id=current_user["auth0_id"],
        profile_data=profile_data
    )
    
    return user
