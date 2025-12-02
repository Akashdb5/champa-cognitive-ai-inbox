"""
Chat Assistant Agent
Processes user queries with access to message history and persona data.
Uses LangChain's create_agent for building a conversational assistant.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from langchain.agents import create_agent, AgentState
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

from app.ai.config import get_ai_config
from app.services.message import MessageService
from app.ai.memory.persona_store import PersonaMemoryStore
from app.models.message import Message


class ChatAssistantAgent:
    """
    Chat assistant agent for processing user queries.
    
    This agent can:
    - Access message history
    - Query persona data
    - Perform semantic search over messages
    - Answer questions about communications
    - Execute actions on behalf of the user
    
    Validates: Requirements 11.2, 11.3
    """
    
    def __init__(
        self,
        db: Session,
        message_service: MessageService,
        persona_store: PersonaMemoryStore
    ):
        """
        Initialize the chat assistant agent
        
        Args:
            db: Database session
            message_service: Message service for accessing message history
            persona_store: Persona store for accessing user preferences
        """
        self.db = db
        self.message_service = message_service
        self.persona_store = persona_store
        self.ai_config = get_ai_config()
        
        # System prompt for the chat assistant
        self.system_prompt = """You are Champa, an intelligent email and communication assistant.

You help users manage their unified inbox by:
- Answering questions about their messages and communications
- Finding specific emails, Slack messages, or calendar events
- Providing summaries and insights about their communications
- Helping them understand priorities and actionable items
- Executing actions like marking items complete or searching messages
- Interacting with Slack channels (list, read, send messages)

You have access to:
- The user's complete message history across Gmail, Slack, and Calendar
- AI-generated summaries and analysis of messages
- User communication preferences and patterns
- Semantic search capabilities to find relevant messages
- Direct Slack integration (list channels, get channel history, send messages)
- Direct Google Calendar integration (list, create, update, delete events)

For Slack interactions, you can:
- List all Slack channels the user has access to
- Get recent message history from any Slack channel
- Send messages to Slack channels or threads
- Answer questions about Slack conversations

For Google Calendar interactions, you can:
- List upcoming calendar events
- Create new calendar events with attendees
- Update existing calendar events
- Delete calendar events
- Answer questions about the user's schedule

When answering questions:
- Be concise but informative
- Reference specific messages when relevant
- Provide actionable insights
- Ask clarifying questions if needed
- Be proactive in suggesting helpful actions
- For Slack queries, use the Slack tools to get real-time information
- For Calendar queries, use the Calendar tools to get real-time information
- When creating events, always confirm details with the user before creating

Always maintain a helpful, professional, and friendly tone.
"""
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create the agent using LangChain's create_agent
        llm = self.ai_config.get_llm()
        self.agent = create_agent(
            model=llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
    
    def _create_tools(self) -> List:
        """Create tools for the chat agent"""
        
        @tool
        def search_messages(query: str, limit: int = 10) -> str:
            """
            Search through messages using semantic search.
            
            Args:
                query: Search query describing what to look for
                limit: Maximum number of results to return (default 10)
            
            Returns:
                String containing search results with message summaries
            """
            # This will be populated with user_id from context
            user_id = self._get_current_user_id()
            
            # Get messages from database with simple text search
            # In production, this would use semantic search via Qdrant
            messages = self.db.query(Message).filter(
                Message.user_id == user_id
            ).order_by(Message.timestamp.desc()).limit(limit).all()
            
            if not messages:
                return "No messages found."
            
            # Format results
            results = []
            for msg in messages:
                result = f"""
Message from {msg.sender} on {msg.timestamp.strftime('%Y-%m-%d %H:%M')}
Platform: {msg.platform}
Subject: {msg.subject or 'N/A'}
Content preview: {msg.content[:200]}...
"""
                results.append(result.strip())
            
            return "\n\n---\n\n".join(results)
        
        @tool
        def get_recent_messages(count: int = 10, platform: Optional[str] = None) -> str:
            """
            Get the most recent messages.
            
            Args:
                count: Number of recent messages to retrieve (default 10)
                platform: Optional platform filter (gmail, slack, calendar)
            
            Returns:
                String containing recent messages with summaries
            """
            user_id = self._get_current_user_id()
            
            query = self.db.query(Message).filter(Message.user_id == user_id)
            
            if platform:
                query = query.filter(Message.platform == platform)
            
            messages = query.order_by(Message.timestamp.desc()).limit(count).all()
            
            if not messages:
                return f"No recent messages found{' for ' + platform if platform else ''}."
            
            results = []
            for msg in messages:
                result = f"""
From: {msg.sender}
Date: {msg.timestamp.strftime('%Y-%m-%d %H:%M')}
Platform: {msg.platform}
Subject: {msg.subject or 'N/A'}
Preview: {msg.content[:150]}...
"""
                results.append(result.strip())
            
            return "\n\n---\n\n".join(results)
        
        @tool
        async def get_user_preferences() -> str:
            """
            Get the user's communication preferences and patterns.
            
            Returns:
                String containing user preferences and style information
            """
            user_id = self._get_current_user_id()
            
            # Get persona data
            persona = await self.persona_store.get_full_persona(user_id)
            
            # Format persona information
            lines = ["User Communication Profile:"]
            
            if persona.get("preferences"):
                lines.append("\nPreferences:")
                for key, value in persona["preferences"].items():
                    lines.append(f"  - {key}: {value}")
            
            if persona.get("style_patterns"):
                patterns = persona["style_patterns"].get("patterns", [])
                if patterns:
                    lines.append("\nCommunication Style:")
                    for pattern in patterns[-3:]:  # Last 3 patterns
                        for key, value in pattern.items():
                            lines.append(f"  - {key}: {value}")
            
            if persona.get("contacts"):
                contacts = persona["contacts"][:5]  # Top 5 contacts
                if contacts:
                    lines.append("\nFrequent Contacts:")
                    for contact in contacts:
                        email = contact.get("email", "unknown")
                        name = contact.get("name", "")
                        count = contact.get("interaction_count", 0)
                        lines.append(f"  - {name or email} ({count} interactions)")
            
            if len(lines) == 1:
                return "No user preferences or patterns recorded yet."
            
            return "\n".join(lines)
        
        @tool
        def get_message_thread(message_id: str) -> str:
            """
            Get the full thread context for a specific message.
            
            Args:
                message_id: The ID of the message to get the thread for
            
            Returns:
                String containing the full message thread
            """
            try:
                from uuid import UUID
                msg_uuid = UUID(message_id)
            except ValueError:
                return f"Invalid message ID format: {message_id}"
            
            thread_context = self.message_service.get_thread_context(msg_uuid, self.db)
            
            if not thread_context:
                return f"No thread found for message {message_id}"
            
            lines = [
                f"Thread: {thread_context.thread_id}",
                f"Participants: {thread_context.participant_count}",
                f"Started: {thread_context.start_time.strftime('%Y-%m-%d %H:%M')}",
                f"Last update: {thread_context.last_update.strftime('%Y-%m-%d %H:%M')}",
                "\nMessages:"
            ]
            
            for msg in thread_context.messages:
                lines.append(f"\n--- From {msg.sender} at {msg.timestamp.strftime('%Y-%m-%d %H:%M')} ---")
                lines.append(f"Subject: {msg.subject or 'N/A'}")
                lines.append(f"Content: {msg.content}")
            
            return "\n".join(lines)
        
        @tool
        def count_messages(platform: Optional[str] = None, days: int = 7) -> str:
            """
            Count messages received in a time period.
            
            Args:
                platform: Optional platform filter (gmail, slack, calendar)
                days: Number of days to look back (default 7)
            
            Returns:
                String with message count statistics
            """
            user_id = self._get_current_user_id()
            
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db.query(Message).filter(
                Message.user_id == user_id,
                Message.timestamp >= cutoff_date
            )
            
            if platform:
                query = query.filter(Message.platform == platform)
            
            count = query.count()
            
            platform_str = f" from {platform}" if platform else ""
            return f"You have received {count} messages{platform_str} in the last {days} days."
        
        @tool
        def mark_actionable_complete(actionable_id: str) -> str:
            """
            Mark an actionable item (task or deadline) as complete.
            
            Args:
                actionable_id: The ID of the actionable item to mark complete
            
            Returns:
                Confirmation message
            
            Validates: Requirements 11.5
            """
            from app.models.message import ActionableItem
            from uuid import UUID
            
            try:
                item_uuid = UUID(actionable_id)
            except ValueError:
                return f"Invalid actionable item ID format: {actionable_id}"
            
            # Get the actionable item
            item = self.db.query(ActionableItem).filter(
                ActionableItem.id == item_uuid
            ).first()
            
            if not item:
                return f"Actionable item {actionable_id} not found."
            
            # Verify it belongs to the current user
            user_id = self._get_current_user_id()
            if str(item.user_id) != user_id:
                return "You don't have permission to modify this item."
            
            # Mark as complete
            item.completed = True
            self.db.commit()
            
            return f"✓ Marked '{item.description}' as complete."
        
        @tool
        def get_actionable_items(completed: bool = False, limit: int = 20) -> str:
            """
            Get actionable items (tasks and deadlines) for the user.
            
            Args:
                completed: Whether to show completed items (default False)
                limit: Maximum number of items to return (default 20)
            
            Returns:
                String containing actionable items
            
            Validates: Requirements 11.5
            """
            from app.models.message import ActionableItem
            
            user_id = self._get_current_user_id()
            
            query = self.db.query(ActionableItem).filter(
                ActionableItem.user_id == user_id,
                ActionableItem.completed == completed
            ).order_by(ActionableItem.deadline.asc().nullslast()).limit(limit)
            
            items = query.all()
            
            if not items:
                status = "completed" if completed else "pending"
                return f"No {status} actionable items found."
            
            lines = [f"{'Completed' if completed else 'Pending'} Actionable Items:"]
            
            for item in items:
                deadline_str = ""
                if item.deadline:
                    deadline_str = f" (Due: {item.deadline.strftime('%Y-%m-%d')})"
                
                status_icon = "✓" if item.completed else "○"
                lines.append(f"{status_icon} [{item.type}] {item.description}{deadline_str}")
                lines.append(f"   ID: {item.id}")
            
            return "\n".join(lines)
        
        @tool
        def get_statistics(days: int = 7) -> str:
            """
            Get statistics about messages and actionable items.
            
            Args:
                days: Number of days to look back (default 7)
            
            Returns:
                String containing statistics
            """
            from app.models.message import ActionableItem
            from datetime import timedelta
            
            user_id = self._get_current_user_id()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count messages by platform
            gmail_count = self.db.query(Message).filter(
                Message.user_id == user_id,
                Message.platform == "gmail",
                Message.timestamp >= cutoff_date
            ).count()
            
            slack_count = self.db.query(Message).filter(
                Message.user_id == user_id,
                Message.platform == "slack",
                Message.timestamp >= cutoff_date
            ).count()
            
            calendar_count = self.db.query(Message).filter(
                Message.user_id == user_id,
                Message.platform == "calendar",
                Message.timestamp >= cutoff_date
            ).count()
            
            # Count actionable items
            pending_items = self.db.query(ActionableItem).filter(
                ActionableItem.user_id == user_id,
                ActionableItem.completed == False
            ).count()
            
            # Count items due today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            due_today = self.db.query(ActionableItem).filter(
                ActionableItem.user_id == user_id,
                ActionableItem.completed == False,
                ActionableItem.deadline >= today_start,
                ActionableItem.deadline < today_end
            ).count()
            
            return f"""Statistics for the last {days} days:

Messages Received:
  - Gmail: {gmail_count}
  - Slack: {slack_count}
  - Calendar: {calendar_count}
  - Total: {gmail_count + slack_count + calendar_count}

Actionable Items:
  - Pending: {pending_items}
  - Due Today: {due_today}
"""
        
        # Import Slack tools manager
        from app.integrations.slack.slack_tools import SlackToolsManager
        
        # Create Slack tools that will use current user context
        @tool
        def list_slack_channels() -> str:
            """List all Slack channels the user has access to. Returns channel names and IDs."""
            user_id = self._get_current_user_id()
            if not user_id:
                return "Error: User context not available"
            manager = SlackToolsManager(self.db, user_id)
            return manager.list_slack_channels()
        
        @tool
        def get_slack_channel_history(channel_id: str, limit: int = 20) -> str:
            """
            Get recent messages from a Slack channel.
            
            Args:
                channel_id: The Slack channel ID (e.g., 'C1234567890') or channel name (e.g., 'general' or '#general')
                limit: Number of messages to fetch (default: 20, max: 100)
            
            Note: If using a channel name, the bot must be a member of that channel.
            Use list_slack_channels first to see available channels.
            """
            user_id = self._get_current_user_id()
            if not user_id:
                return "Error: User context not available"
            manager = SlackToolsManager(self.db, user_id)
            return manager.get_slack_channel_history(channel_id, limit)
        
        @tool
        def send_slack_message(channel_id: str, text: str, thread_ts: str = None) -> str:
            """
            Send a message to a Slack channel.
            
            Args:
                channel_id: The Slack channel ID (e.g., 'C1234567890')
                text: The message text to send
                thread_ts: Optional thread timestamp to reply in a thread
            """
            user_id = self._get_current_user_id()
            if not user_id:
                return "Error: User context not available"
            manager = SlackToolsManager(self.db, user_id)
            return manager.send_slack_message(channel_id, text, thread_ts)
        
        # Import Google Calendar tools manager
        from app.integrations.google.calendar_tools import CalendarToolsManager
        
        # Create Calendar tools that will use current user context
        @tool
        def list_calendar_events(limit: int = 10, date_from: str = None) -> str:
            """
            List upcoming events from Google Calendar.
            
            Args:
                limit: Number of events to return (default: 10)
                date_from: Start date in ISO format (default: today)
            
            Returns:
                JSON string with list of events including title, time, location, and attendees
            """
            user_id = self._get_current_user_id()
            if not user_id:
                return "Error: User context not available"
            manager = CalendarToolsManager(self.db, user_id)
            return manager.list_events(limit, date_from)
        
        @tool
        def create_calendar_event(
            start_datetime: str,
            end_datetime: str,
            title: str = None,
            description: str = None,
            location: str = None,
            timezone: str = None,
            attendees: List[str] = None
        ) -> str:
            """
            Create a new event in Google Calendar.
            
            Args:
                start_datetime: Start date and time in ISO format (e.g., '2024-12-01T10:00:00')
                end_datetime: End date and time in ISO format (e.g., '2024-12-01T11:00:00')
                title: Title of the event
                description: Detailed description
                location: Location of the event
                timezone: Timezone (default: UTC)
                attendees: List of attendee email addresses
            
            Returns:
                JSON string with created event details
            """
            user_id = self._get_current_user_id()
            if not user_id:
                return "Error: User context not available"
            manager = CalendarToolsManager(self.db, user_id)
            return manager.create_event(
                start_datetime, end_datetime, title, description,
                location, timezone, attendees
            )
        
        @tool
        def update_calendar_event(
            event_id: str,
            start_datetime: str = None,
            end_datetime: str = None,
            title: str = None,
            description: str = None,
            location: str = None,
            timezone: str = None,
            attendees: List[str] = None
        ) -> str:
            """
            Update an existing event in Google Calendar.
            
            Args:
                event_id: The Google Calendar event ID
                start_datetime: New start date and time in ISO format (optional)
                end_datetime: New end date and time in ISO format (optional)
                title: New title (optional)
                description: New description (optional)
                location: New location (optional)
                timezone: New timezone (optional)
                attendees: New list of attendee email addresses (optional)
            
            Returns:
                JSON string with updated event details
            """
            user_id = self._get_current_user_id()
            if not user_id:
                return "Error: User context not available"
            manager = CalendarToolsManager(self.db, user_id)
            return manager.update_event(
                event_id, start_datetime, end_datetime, title,
                description, location, timezone, attendees
            )
        
        @tool
        def delete_calendar_event(event_id: str) -> str:
            """
            Delete an event from Google Calendar.
            
            Args:
                event_id: The Google Calendar event ID
            
            Returns:
                JSON string with deletion result
            """
            user_id = self._get_current_user_id()
            if not user_id:
                return "Error: User context not available"
            manager = CalendarToolsManager(self.db, user_id)
            return manager.delete_event(event_id)
        
        return [
            search_messages,
            get_recent_messages,
            get_user_preferences,
            get_message_thread,
            count_messages,
            mark_actionable_complete,
            get_actionable_items,
            get_statistics,
            list_slack_channels,
            get_slack_channel_history,
            send_slack_message,
            list_calendar_events,
            create_calendar_event,
            update_calendar_event,
            delete_calendar_event
        ]
    
    def _get_current_user_id(self) -> str:
        """Get the current user ID from context"""
        # This will be set when processing a query
        return getattr(self, '_current_user_id', None)
    
    async def process_query(
        self,
        user_id: str,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a user query and generate a response
        
        Args:
            user_id: User ID making the query
            query: The user's question or request
            conversation_history: Optional previous messages in the conversation
        
        Returns:
            str: The assistant's response
        
        Validates: Requirements 11.2, 11.3, 11.4
        """
        # Set current user ID for tools to access
        self._current_user_id = user_id
        
        # Build message history
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        # Invoke the agent
        result = await self.agent.ainvoke(
            {"messages": messages},
            config={"configurable": {"user_id": user_id}}
        )
        
        # Extract the response
        response_messages = result.get("messages", [])
        if response_messages:
            last_message = response_messages[-1]
            if hasattr(last_message, "content"):
                return last_message.content
            elif isinstance(last_message, dict):
                return last_message.get("content", "")
        
        return "I'm sorry, I couldn't process that request."


def get_chat_agent(
    db: Session,
    message_service: MessageService,
    persona_store: PersonaMemoryStore
) -> ChatAssistantAgent:
    """
    Get or create a chat assistant agent instance
    
    Args:
        db: Database session
        message_service: Message service
        persona_store: Persona store
    
    Returns:
        ChatAssistantAgent: Configured chat agent
    """
    return ChatAssistantAgent(
        db=db,
        message_service=message_service,
        persona_store=persona_store
    )
