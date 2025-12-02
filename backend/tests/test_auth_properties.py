"""
Property-based tests for Auth0 authentication system

Feature: champa-unified-inbox
Tests Properties for Auth0 token verification and user management
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from jose import jwt

from app.core.database import Base, get_db
from app.models.user import User
from app.core.config import settings
from main import app

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Hypothesis strategies for generating test data
valid_username_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
    min_size=3,
    max_size=20
)

valid_email_strategy = st.builds(
    lambda name, domain: f"{name}@{domain}.com",
    name=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=3, max_size=10),
    domain=st.text(alphabet=st.characters(whitelist_categories=("Ll",)), min_size=3, max_size=10)
)

auth0_id_strategy = st.builds(
    lambda provider, id: f"{provider}|{id}",
    provider=st.sampled_from(["auth0", "google-oauth2", "facebook", "twitter"]),
    id=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=10, max_size=30)
)


def create_test_user(db, username: str, email: str, auth0_id: str) -> User:
    """Helper to create a test user with Auth0 ID"""
    user = User(
        id=uuid.uuid4(),
        username=username,
        email=email,
        auth0_id=auth0_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_mock_auth0_token(user_id: str, email: str, username: str) -> str:
    """Create a mock Auth0 JWT token for testing"""
    payload = {
        "sub": user_id,
        "email": email,
        "name": username,
        "aud": settings.AUTH0_API_AUDIENCE,
        "iss": f"https://{settings.AUTH0_DOMAIN}/",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    # Use HS256 for testing (in production Auth0 uses RS256)
    return jwt.encode(payload, "test-secret", algorithm="HS256")


# Property 1: Valid Auth0 tokens grant access
# Feature: champa-unified-inbox, Property 1: Valid Auth0 tokens grant access
@given(
    username=valid_username_strategy,
    email=valid_email_strategy,
    auth0_id=auth0_id_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_1_valid_auth0_tokens_grant_access(setup_database, username, email, auth0_id):
    """
    **Feature: champa-unified-inbox, Property 1: Valid Auth0 tokens grant access**
    **Validates: Requirements 1.2**
    
    For any valid Auth0 token, the user should be able to access protected routes
    and their user record should be created/synced in the database.
    """
    db = TestingSessionLocal()
    try:
        # Create mock Auth0 token
        token = create_mock_auth0_token(auth0_id, email, username)
        
        # Mock the verify_token function to accept our test token
        with patch('app.core.security.verify_token') as mock_verify:
            mock_verify.return_value = {
                "sub": auth0_id,
                "email": email,
                "name": username
            }
            
            # Access protected route with valid token
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should succeed
            assert response.status_code == 200
            data = response.json()
            
            # Verify user info is returned
            assert data["email"] == email
            assert data["username"] == username
            
            # Verify user was created in database
            user = db.query(User).filter(User.auth0_id == auth0_id).first()
            assert user is not None
            assert user.email == email
        
    finally:
        db.close()


# Property 2: Invalid tokens are rejected
# Feature: champa-unified-inbox, Property 2: Invalid tokens are rejected
@given(
    invalid_token=st.text(min_size=10, max_size=100)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_2_invalid_tokens_rejected(setup_database, invalid_token):
    """
    **Feature: champa-unified-inbox, Property 2: Invalid tokens are rejected**
    **Validates: Requirements 1.3**
    
    For any invalid token (malformed, expired, wrong signature), 
    authentication should fail and return an error.
    """
    db = TestingSessionLocal()
    try:
        # Attempt to access protected route with invalid token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        
        # Should fail with 401 Unauthorized
        assert response.status_code == 401
        
    finally:
        db.close()


# Property 3: Protected routes require valid tokens
# Feature: champa-unified-inbox, Property 3: Protected routes require valid tokens
@given(
    username=valid_username_strategy,
    email=valid_email_strategy,
    auth0_id=auth0_id_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_3_protected_routes_require_valid_tokens(setup_database, username, email, auth0_id):
    """
    **Feature: champa-unified-inbox, Property 3: Protected routes require valid tokens**
    **Validates: Requirements 1.4**
    
    For any protected route and any request, access should only be granted 
    if a valid Auth0 token is provided in the request headers.
    """
    db = TestingSessionLocal()
    try:
        # Test 1: Access protected route without token
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # Forbidden (no credentials)
        
        # Test 2: Access with invalid token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401  # Unauthorized
        
        # Test 3: Create valid Auth0 token
        token = create_mock_auth0_token(auth0_id, email, username)
        
        # Mock the verify_token function
        with patch('app.core.security.verify_token') as mock_verify:
            mock_verify.return_value = {
                "sub": auth0_id,
                "email": email,
                "name": username
            }
            
            # Test 4: Access with valid token should succeed
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == email
        
    finally:
        db.close()


# Property 4: User sync maintains data consistency
# Feature: champa-unified-inbox, Property 4: User sync maintains data consistency
@given(
    username=valid_username_strategy,
    email=valid_email_strategy,
    auth0_id=auth0_id_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_4_user_sync_maintains_consistency(setup_database, username, email, auth0_id):
    """
    **Feature: champa-unified-inbox, Property 4: User sync maintains data consistency**
    **Validates: Requirements 1.5**
    
    For any Auth0 user, accessing the API should create or update their user record
    in the database, maintaining consistency between Auth0 and local data.
    """
    db = TestingSessionLocal()
    try:
        # Create mock Auth0 token
        token = create_mock_auth0_token(auth0_id, email, username)
        
        # Mock the verify_token function
        with patch('app.core.security.verify_token') as mock_verify:
            mock_verify.return_value = {
                "sub": auth0_id,
                "email": email,
                "name": username
            }
            
            # First access - should create user
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            
            # Verify user was created
            user = db.query(User).filter(User.auth0_id == auth0_id).first()
            assert user is not None
            assert user.email == email
            assert user.username == username
            user_id = user.id
            
            # Second access with updated info
            new_username = username + "_updated"
            mock_verify.return_value = {
                "sub": auth0_id,
                "email": email,
                "name": new_username
            }
            
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            
            # Verify user was updated, not duplicated
            db.expire_all()  # Clear cache
            user = db.query(User).filter(User.auth0_id == auth0_id).first()
            assert user is not None
            assert user.id == user_id  # Same user
            assert user.username == new_username  # Updated username
            
            # Verify no duplicate users
            user_count = db.query(User).filter(User.auth0_id == auth0_id).count()
            assert user_count == 1
        
    finally:
        db.close()
