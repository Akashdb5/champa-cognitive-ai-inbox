"""
Authentication service for Auth0 user management
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import auth0_client
from app.models.user import User


class AuthService:
    """Service for handling Auth0 authentication and user management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """
        Logout a user by revoking their refresh token
        
        Args:
            refresh_token: Optional refresh token to revoke
        """
        if refresh_token:
            try:
                await auth0_client.revoke_token(refresh_token)
            except Exception:
                # Log error but don't fail logout
                pass
    
    def get_or_create_user(self, auth0_id: str, email: Optional[str] = None, username: Optional[str] = None) -> User:
        """
        Get existing user or create new user from Auth0 data
        
        Args:
            auth0_id: Auth0 user ID (sub claim)
            email: Optional user email
            username: Optional username
        
        Returns:
            User object
        """
        # Try to find existing user by Auth0 ID
        user = self.db.query(User).filter(User.auth0_id == auth0_id).first()
        
        if user:
            # Update user info if changed
            if email and user.email != email:
                user.email = email
            if username and user.username != username:
                user.username = username
            self.db.commit()
            self.db.refresh(user)
            return user
        
        # Try to find by email (for migration of existing users)
        if email:
            user = self.db.query(User).filter(User.email == email).first()
            if user:
                # Link existing user to Auth0
                user.auth0_id = auth0_id
                if username and not user.username:
                    user.username = username
                self.db.commit()
                self.db.refresh(user)
                return user
        
        # Create new user - generate defaults if email/username not provided
        if not email:
            # Generate a placeholder email from auth0_id
            email = f"{auth0_id.replace('|', '_')}@auth0.user"
        
        if not username:
            username = email.split('@')[0]
        
        user = User(
            email=email,
            username=username,
            auth0_id=auth0_id
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_auth0_id(self, auth0_id: str) -> Optional[User]:
        """Get user by Auth0 ID"""
        return self.db.query(User).filter(User.auth0_id == auth0_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user_profile(self, auth0_id: str, profile_data) -> User:
        """
        Update user profile fields
        
        Args:
            auth0_id: Auth0 user ID
            profile_data: UserUpdate schema with profile fields
        
        Returns:
            Updated User object
        """
        user = self.get_user_by_auth0_id(auth0_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only provided fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
