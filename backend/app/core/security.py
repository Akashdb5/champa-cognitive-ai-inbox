"""
Security utilities for Auth0 integration and JWT token handling
"""
from datetime import datetime
from typing import Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

from app.core.config import settings

# HTTP Bearer token scheme
security = HTTPBearer()

# JWT Configuration
ALGORITHM = "RS256"


class Auth0Client:
    """Auth0 client for authentication operations"""
    
    def __init__(self):
        self.domain = settings.AUTH0_DOMAIN
        self.client_id = settings.AUTH0_CLIENT_ID
        self.client_secret = settings.AUTH0_CLIENT_SECRET
        self.audience = settings.AUTH0_API_AUDIENCE
        self._jwks_cache = None
        self._jwks_cache_time = None
        
    async def get_jwks(self) -> Dict[str, Any]:
        """Fetch JSON Web Key Set from Auth0 with caching and timeout handling"""
        import time
        
        # Return cached JWKS if less than 1 hour old
        if self._jwks_cache and self._jwks_cache_time:
            if time.time() - self._jwks_cache_time < 3600:  # 1 hour cache
                return self._jwks_cache
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:  # 10 second timeout
                response = await client.get(f"https://{self.domain}/.well-known/jwks.json")
                response.raise_for_status()
                jwks = response.json()
                
                # Cache the result
                self._jwks_cache = jwks
                self._jwks_cache_time = time.time()
                
                return jwks
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
            # If we have cached JWKS, use it even if expired
            if self._jwks_cache:
                print(f"Warning: Auth0 connection failed, using cached JWKS: {e}")
                return self._jwks_cache
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth0 service temporarily unavailable"
            )
    
    async def revoke_token(self, token: str) -> None:
        """Revoke a refresh token"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"https://{self.domain}/oauth/revoke",
                    json={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "token": token
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Token revocation failed"
                    )
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
            print(f"Warning: Auth0 token revocation failed: {e}")
            # Don't fail the request if revocation fails
            pass


# Global Auth0 client instance
auth0_client = Auth0Client()


async def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode an Auth0 JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get unverified header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
        
        # Fetch JWKS from Auth0
        jwks = await auth0_client.get_jwks()
        
        # Find the matching key
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise credentials_exception
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[ALGORITHM],
            audience=settings.AUTH0_API_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/"
        )
        return payload
        
    except JWTError as e:
        raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user from Auth0 token"""
    token = credentials.credentials
    payload = await verify_token(token)
    
    # Extract user info from Auth0 token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return {
        "auth0_id": user_id,
        "email": payload.get("email"),
        "username": payload.get("name") or payload.get("nickname") or payload.get("email")
    }
