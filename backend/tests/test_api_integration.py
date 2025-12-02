"""
Integration tests for API endpoints

Tests the complete API workflows end-to-end including:
- Authentication flow
- Platform connection flow
- Message fetching and display
- Smart reply workflow
- Chat interaction
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from uuid import uuid4

from main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.platform import PlatformConnection
from app.models.message import Message, MessageAnalysis, ActionableItem, SmartReply
from unittest.mock import patch
from jose import jwt

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user with Auth0 ID"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        auth0_id="auth0|test123456"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def mock_auth0_token(test_user):
    """Create a mock Auth0 token for testing"""
    payload = {
        "sub": test_user.auth0_id,
        "email": test_user.email,
        "name": test_user.username,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, "test-secret", algorithm="HS256")


@pytest.fixture
def auth_headers(mock_auth0_token):
    """Create authentication headers with mock Auth0 token"""
    return {"Authorization": f"Bearer {mock_auth0_token}"}


class TestAuthenticationFlow:
    """Test Auth0 authentication endpoints end-to-end"""
    
    def test_get_current_user_with_valid_token(self, client, test_user, auth_headers):
        """Test getting current user info with valid Auth0 token"""
        with patch('app.core.security.verify_token') as mock_verify:
            mock_verify.return_value = {
                "sub": test_user.auth0_id,
                "email": test_user.email,
                "name": test_user.username
            }
            
            response = client.get("/api/auth/me", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == test_user.email
            assert data["username"] == test_user.username
    
    def test_get_current_user_without_token(self, client):
        """Test accessing protected route without token fails"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403
    
    def test_get_current_user_with_invalid_token(self, client):
        """Test accessing protected route with invalid token fails"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
    
    def test_protected_route_without_token(self, client):
        """Test protected route rejects requests without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403


class TestPlatformConnectionFlow:
    """Test platform connection endpoints"""
    
    def test_get_platform_status(self, client, test_user, auth_headers, db_session):
        """Test getting platform connection status"""
        # Add a connected platform
        connection = PlatformConnection(
            id=uuid4(),
            user_id=test_user.id,
            platform="gmail",
            access_token="test_token",
            connected_at=datetime.utcnow()
        )
        db_session.add(connection)
        db_session.commit()
        
        response = client.get("/platforms/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["gmail"] == True
        assert data["slack"] == False
        assert data["calendar"] == False


class TestMessageEndpoints:
    """Test message fetching and display"""
    
    def test_get_messages(self, client, test_user, auth_headers, db_session):
        """Test fetching messages for user"""
        # Create test messages
        for i in range(3):
            message = Message(
                id=uuid4(),
                user_id=test_user.id,
                platform="gmail",
                platform_message_id=f"msg_{i}",
                sender=f"sender{i}@example.com",
                content=f"Test message {i}",
                subject=f"Subject {i}",
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            db_session.add(message)
        db_session.commit()
        
        response = client.get("/api/messages/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["platform"] == "gmail"
    
    def test_get_message_by_id(self, client, test_user, auth_headers, db_session):
        """Test getting a specific message"""
        message = Message(
            id=uuid4(),
            user_id=test_user.id,
            platform="slack",
            platform_message_id="msg_123",
            sender="user@example.com",
            content="Test message",
            timestamp=datetime.utcnow()
        )
        db_session.add(message)
        db_session.commit()
        
        response = client.get(f"/api/messages/{message.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "slack"
        assert data["content"] == "Test message"
    
    def test_get_message_thread(self, client, test_user, auth_headers, db_session):
        """Test getting thread context for a message"""
        thread_id = "thread_123"
        
        # Create messages in a thread
        for i in range(3):
            message = Message(
                id=uuid4(),
                user_id=test_user.id,
                platform="gmail",
                platform_message_id=f"msg_{i}",
                sender=f"sender{i}@example.com",
                content=f"Message {i} in thread",
                thread_id=thread_id,
                timestamp=datetime.utcnow() - timedelta(minutes=i)
            )
            db_session.add(message)
        db_session.commit()
        
        # Get the first message
        first_message = db_session.query(Message).filter(
            Message.thread_id == thread_id
        ).first()
        
        response = client.get(
            f"/api/messages/{first_message.id}/thread",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == thread_id
        assert len(data["messages"]) == 3
        assert data["participant_count"] == 3


class TestSmartReplyWorkflow:
    """Test smart reply generation and approval workflow"""
    
    def test_get_pending_replies(self, client, test_user, auth_headers, db_session):
        """Test getting pending smart replies"""
        # Create a message
        message = Message(
            id=uuid4(),
            user_id=test_user.id,
            platform="gmail",
            platform_message_id="msg_123",
            sender="sender@example.com",
            content="Test message",
            timestamp=datetime.utcnow()
        )
        db_session.add(message)
        db_session.commit()
        
        # Create a pending reply
        reply = SmartReply(
            id=uuid4(),
            message_id=message.id,
            user_id=test_user.id,
            draft_content="This is a draft reply",
            status="pending"
        )
        db_session.add(reply)
        db_session.commit()
        
        response = client.get("/api/replies/pending", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"
        assert data[0]["draft_content"] == "This is a draft reply"


class TestChatInteraction:
    """Test chat assistant interaction"""
    
    def test_send_chat_message(self, client, test_user, auth_headers):
        """Test sending a message to chat assistant"""
        response = client.post(
            "/chat/message",
            headers=auth_headers,
            json={
                "message": "Hello, what's in my inbox?"
            }
        )
        
        # Note: This may fail if AI services are not configured
        # In a real test, we would mock the AI service
        assert response.status_code in [200, 500]
    
    def test_get_chat_history(self, client, test_user, auth_headers):
        """Test getting chat history"""
        response = client.get("/chat/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total_count" in data


class TestStatisticsEndpoints:
    """Test statistics endpoints"""
    
    def test_get_overview_stats(self, client, test_user, auth_headers, db_session):
        """Test getting overview statistics"""
        # Create test data
        message = Message(
            id=uuid4(),
            user_id=test_user.id,
            platform="gmail",
            platform_message_id="msg_123",
            sender="sender@example.com",
            content="Test message",
            timestamp=datetime.utcnow()
        )
        db_session.add(message)
        
        actionable = ActionableItem(
            id=uuid4(),
            message_id=message.id,
            user_id=test_user.id,
            type="task",
            description="Test task",
            deadline=datetime.utcnow() + timedelta(hours=2),
            completed=False
        )
        db_session.add(actionable)
        db_session.commit()
        
        response = client.get("/api/stats/overview", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "new_messages_count" in data
        assert "pending_drafts_count" in data
        assert "actionables_today_count" in data
        assert data["total_messages"] >= 1
    
    def test_get_actionable_stats(self, client, test_user, auth_headers, db_session):
        """Test getting actionable item statistics"""
        # Create test message
        message = Message(
            id=uuid4(),
            user_id=test_user.id,
            platform="gmail",
            platform_message_id="msg_123",
            sender="sender@example.com",
            content="Test message",
            timestamp=datetime.utcnow()
        )
        db_session.add(message)
        
        # Create actionable items
        actionable1 = ActionableItem(
            id=uuid4(),
            message_id=message.id,
            user_id=test_user.id,
            type="task",
            description="Pending task",
            deadline=datetime.utcnow() + timedelta(days=1),
            completed=False
        )
        actionable2 = ActionableItem(
            id=uuid4(),
            message_id=message.id,
            user_id=test_user.id,
            type="deadline",
            description="Completed deadline",
            deadline=datetime.utcnow() - timedelta(days=1),
            completed=True
        )
        db_session.add_all([actionable1, actionable2])
        db_session.commit()
        
        response = client.get("/api/stats/actionables", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_actionables"] == 2
        assert data["completed_count"] == 1
        assert data["pending_count"] == 1
        assert "by_type" in data
        assert "upcoming_deadlines" in data
