"""
Integration tests for Chat Assistant Agent
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from uuid import uuid4

from app.ai.agents.chat import ChatAssistantAgent, get_chat_agent
from app.services.message import MessageService
from app.ai.memory.persona_store import PersonaMemoryStore
from app.models.message import Message, ActionableItem


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    db = Mock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    return db


@pytest.fixture
def mock_message_service():
    """Create a mock message service"""
    return Mock(spec=MessageService)


@pytest.fixture
def mock_persona_store():
    """Create a mock persona store"""
    store = Mock(spec=PersonaMemoryStore)
    store.get_full_persona = AsyncMock(return_value={
        "preferences": {"tone": "professional"},
        "style_patterns": {"patterns": []},
        "contacts": []
    })
    return store


@pytest.fixture
def chat_agent(mock_db, mock_message_service, mock_persona_store):
    """Create a chat agent instance for testing"""
    return ChatAssistantAgent(
        db=mock_db,
        message_service=mock_message_service,
        persona_store=mock_persona_store
    )


def test_chat_agent_initialization(chat_agent):
    """Test that chat agent initializes correctly"""
    assert chat_agent is not None
    assert chat_agent.db is not None
    assert chat_agent.message_service is not None
    assert chat_agent.persona_store is not None
    assert chat_agent.agent is not None
    assert len(chat_agent.tools) == 8  # Should have 8 tools


def test_get_chat_agent_factory(mock_db, mock_message_service, mock_persona_store):
    """Test the factory function for creating chat agents"""
    agent = get_chat_agent(mock_db, mock_message_service, mock_persona_store)
    assert isinstance(agent, ChatAssistantAgent)


@pytest.mark.asyncio
async def test_process_query_basic(chat_agent, mock_db):
    """Test basic query processing"""
    user_id = str(uuid4())
    
    # Mock the agent's ainvoke method
    mock_response = {
        "messages": [
            Mock(content="I can help you with that!")
        ]
    }
    chat_agent.agent.ainvoke = AsyncMock(return_value=mock_response)
    
    # Process a simple query
    response = await chat_agent.process_query(
        user_id=user_id,
        query="Hello, can you help me?",
        conversation_history=None
    )
    
    assert response == "I can help you with that!"
    assert chat_agent._current_user_id == user_id


@pytest.mark.asyncio
async def test_process_query_with_history(chat_agent):
    """Test query processing with conversation history"""
    user_id = str(uuid4())
    
    conversation_history = [
        {"role": "user", "content": "What's my email count?"},
        {"role": "assistant", "content": "You have 10 emails."}
    ]
    
    # Mock the agent's ainvoke method
    mock_response = {
        "messages": [
            Mock(content="You have 5 new emails since then.")
        ]
    }
    chat_agent.agent.ainvoke = AsyncMock(return_value=mock_response)
    
    response = await chat_agent.process_query(
        user_id=user_id,
        query="How many new ones?",
        conversation_history=conversation_history
    )
    
    assert response == "You have 5 new emails since then."


def test_tool_count_messages(chat_agent, mock_db):
    """Test the count_messages tool"""
    user_id = str(uuid4())
    chat_agent._current_user_id = user_id
    
    # Mock database query
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 15
    mock_db.query.return_value = mock_query
    
    # Get the count_messages tool
    count_tool = next(t for t in chat_agent.tools if t.name == "count_messages")
    
    # Execute the tool
    result = count_tool.func(platform=None, days=7)
    
    assert "15 messages" in result
    assert "last 7 days" in result


def test_tool_get_actionable_items(chat_agent, mock_db):
    """Test the get_actionable_items tool"""
    user_id = str(uuid4())
    chat_agent._current_user_id = user_id
    
    # Create mock actionable items
    mock_item1 = Mock(spec=ActionableItem)
    mock_item1.id = uuid4()
    mock_item1.type = "task"
    mock_item1.description = "Review document"
    mock_item1.deadline = None
    mock_item1.completed = False
    
    mock_item2 = Mock(spec=ActionableItem)
    mock_item2.id = uuid4()
    mock_item2.type = "deadline"
    mock_item2.description = "Submit report"
    mock_item2.deadline = datetime(2024, 12, 1)
    mock_item2.completed = False
    
    # Mock database query
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [mock_item1, mock_item2]
    mock_db.query.return_value = mock_query
    
    # Get the tool
    get_items_tool = next(t for t in chat_agent.tools if t.name == "get_actionable_items")
    
    # Execute the tool
    result = get_items_tool.func(completed=False, limit=20)
    
    assert "Pending Actionable Items" in result
    assert "Review document" in result
    assert "Submit report" in result
    assert "2024-12-01" in result


def test_tool_mark_actionable_complete(chat_agent, mock_db):
    """Test the mark_actionable_complete tool"""
    user_id = str(uuid4())
    chat_agent._current_user_id = user_id
    
    item_id = uuid4()
    
    # Create mock actionable item
    mock_item = Mock(spec=ActionableItem)
    mock_item.id = item_id
    mock_item.user_id = user_id
    mock_item.description = "Test task"
    mock_item.completed = False
    
    # Mock database query
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_item
    mock_db.query.return_value = mock_query
    
    # Get the tool
    mark_complete_tool = next(t for t in chat_agent.tools if t.name == "mark_actionable_complete")
    
    # Execute the tool
    result = mark_complete_tool.func(actionable_id=str(item_id))
    
    assert "✓" in result
    assert "Test task" in result
    assert "complete" in result.lower()
    assert mock_item.completed == True
    mock_db.commit.assert_called_once()


def test_tool_get_statistics(chat_agent, mock_db):
    """Test the get_statistics tool"""
    user_id = str(uuid4())
    chat_agent._current_user_id = user_id
    
    # Mock database queries for message counts
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 5  # Return 5 for all counts
    mock_db.query.return_value = mock_query
    
    # Get the tool
    stats_tool = next(t for t in chat_agent.tools if t.name == "get_statistics")
    
    # Execute the tool
    result = stats_tool.func(days=7)
    
    assert "Statistics" in result
    assert "Gmail:" in result
    assert "Slack:" in result
    assert "Calendar:" in result
    assert "Pending:" in result
    assert "Due Today:" in result


def test_tool_search_messages(chat_agent, mock_db):
    """Test the search_messages tool"""
    user_id = str(uuid4())
    chat_agent._current_user_id = user_id
    
    # Create mock messages
    mock_msg = Mock(spec=Message)
    mock_msg.sender = "test@example.com"
    mock_msg.timestamp = datetime(2024, 11, 29, 10, 0)
    mock_msg.platform = "gmail"
    mock_msg.subject = "Test Subject"
    mock_msg.content = "This is a test message content"
    
    # Mock database query
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [mock_msg]
    mock_db.query.return_value = mock_query
    
    # Get the tool
    search_tool = next(t for t in chat_agent.tools if t.name == "search_messages")
    
    # Execute the tool
    result = search_tool.func(query="test", limit=10)
    
    assert "test@example.com" in result
    assert "gmail" in result
    assert "Test Subject" in result


def test_tool_get_recent_messages(chat_agent, mock_db):
    """Test the get_recent_messages tool"""
    user_id = str(uuid4())
    chat_agent._current_user_id = user_id
    
    # Create mock message
    mock_msg = Mock(spec=Message)
    mock_msg.sender = "sender@example.com"
    mock_msg.timestamp = datetime(2024, 11, 29, 15, 30)
    mock_msg.platform = "slack"
    mock_msg.subject = None
    mock_msg.content = "Recent slack message"
    
    # Mock database query
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [mock_msg]
    mock_db.query.return_value = mock_query
    
    # Get the tool
    recent_tool = next(t for t in chat_agent.tools if t.name == "get_recent_messages")
    
    # Execute the tool
    result = recent_tool.func(count=10, platform="slack")
    
    assert "sender@example.com" in result
    assert "slack" in result
    assert "Recent slack message" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
