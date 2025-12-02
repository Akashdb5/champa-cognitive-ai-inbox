"""
Integration tests for Deep Agent and Smart Reply functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from app.ai.agents.deep_agent import SmartReplyDeepAgent, get_smart_reply_agent
from app.ai.memory.persona_store import PersonaMemoryStore, get_persona_store
from app.services.reply import SmartReplyService, get_reply_service


class TestDeepAgentIntegration:
    """Test deep agent initialization and basic functionality"""
    
    def test_deep_agent_initialization(self):
        """Test that deep agent can be initialized"""
        agent = get_smart_reply_agent()
        assert agent is not None
        assert isinstance(agent, SmartReplyDeepAgent)
        assert agent.agent is not None
        assert agent.store is not None
    
    def test_persona_store_initialization(self):
        """Test that persona store can be initialized"""
        mock_db = Mock()
        store = get_persona_store(mock_db)
        assert store is not None
        assert isinstance(store, PersonaMemoryStore)
        assert store.db is mock_db
        assert store.store is not None
    
    def test_reply_service_initialization(self):
        """Test that reply service can be initialized"""
        mock_db = Mock()
        service = get_reply_service(mock_db)
        assert service is not None
        assert isinstance(service, SmartReplyService)
        assert service.db is mock_db
        assert service.deep_agent is not None
        assert service.persona_store is not None


class TestPersonaMemoryStore:
    """Test persona memory store functionality"""
    
    @pytest.mark.asyncio
    async def test_store_observation(self):
        """Test storing an observation"""
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        store = PersonaMemoryStore(mock_db)
        
        user_id = str(uuid4())
        observation_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "tone": "professional",
            "length": "concise"
        }
        
        await store.store_observation(
            user_id=user_id,
            observation_type="style_pattern",
            observation_data=observation_data
        )
        
        # Verify database interaction
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_retrieve_style_patterns_empty(self):
        """Test retrieving style patterns when none exist"""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        store = PersonaMemoryStore(mock_db)
        
        user_id = str(uuid4())
        patterns = await store.retrieve_style_patterns(user_id)
        
        assert patterns == {"patterns": []}
    
    @pytest.mark.asyncio
    async def test_get_full_persona(self):
        """Test getting full persona data"""
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        store = PersonaMemoryStore(mock_db)
        
        user_id = str(uuid4())
        persona = await store.get_full_persona(user_id)
        
        assert "style_patterns" in persona
        assert "contacts" in persona
        assert "preferences" in persona


class TestSmartReplyService:
    """Test smart reply service functionality"""
    
    @pytest.mark.asyncio
    async def test_fetch_thread_context_single_message(self):
        """Test fetching thread context for a single message"""
        mock_db = Mock()
        
        # Create mock message
        message_id = uuid4()
        mock_message = Mock()
        mock_message.id = message_id
        mock_message.platform = "gmail"
        mock_message.thread_id = None
        mock_message.sender = "test@example.com"
        mock_message.subject = "Test Subject"
        mock_message.content = "Test content"
        mock_message.timestamp = datetime.utcnow()
        
        # Setup query mock
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_message
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_message]
        mock_db.query.return_value = mock_query
        
        service = SmartReplyService(mock_db)
        
        context = await service.fetch_thread_context(message_id)
        
        assert context is not None
        assert "gmail" in context
        assert "test@example.com" in context
        assert "Test Subject" in context
        assert "Test content" in context
    
    def test_get_pending_replies_empty(self):
        """Test getting pending replies when none exist"""
        mock_db = Mock()
        
        # Setup query mock
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        service = SmartReplyService(mock_db)
        
        user_id = uuid4()
        replies = service.get_pending_replies(user_id)
        
        assert replies == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
