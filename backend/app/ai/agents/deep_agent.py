"""
Deep Agent for Smart Reply Generation
Uses LangGraph's create_deep_agent with planning, filesystem, and subagent capabilities.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from langgraph.store.memory import InMemoryStore
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

from app.ai.config import get_ai_config


class SmartReplyDeepAgent:
    """
    Deep agent for generating smart replies with planning and memory capabilities.
    
    This agent uses LangGraph's deep agent architecture with:
    - Planning middleware (TodoListMiddleware) for breaking down reply generation
    - Filesystem middleware (FilesystemMiddleware) for context storage
    - Subagent middleware (SubAgentMiddleware) for delegating subtasks
    - Long-term memory via LangGraph Store for user persona
    """
    
    def __init__(self, store: Optional[InMemoryStore] = None):
        """
        Initialize the deep agent
        
        Args:
            store: LangGraph Store for long-term memory (defaults to InMemoryStore)
        """
        self.store = store or InMemoryStore()
        self.ai_config = get_ai_config()
        
        # System prompt for smart reply generation
        self.system_prompt = """You are an expert email assistant that generates context-aware draft replies.

Your job is to:
1. Analyze the email thread context thoroughly
2. Retrieve the user's communication style and preferences from memory
3. Plan your response approach step-by-step
4. Generate a draft reply that matches the user's style and addresses all points
5. Format the reply appropriately for the platform (Gmail, Slack, etc.)

## Memory System

You have access to long-term memory stored in /memories/ where you can:
- Read user preferences and communication style patterns
- Access information about recurring contacts and relationships
- Retrieve past interaction patterns

Always check /memories/user_preferences.txt and /memories/communication_style.txt before generating replies.

## Planning

Use the write_todos tool to break down complex reply generation into steps:
1. Understand the context and what needs to be addressed
2. Retrieve relevant persona information
3. Draft the core message
4. Refine tone and style
5. Format for the target platform

## Context Management

Use filesystem tools to manage large contexts:
- write_file: Store thread context or research
- read_file: Retrieve stored context
- edit_file: Update drafts iteratively

## Guidelines

- Match the user's communication style (formal vs casual, length, tone)
- Address all points raised in the original message
- Be concise but complete
- Use appropriate greetings and sign-offs based on the relationship
- Maintain professional boundaries while being personable
"""
        
        # Get LLM model
        llm = self.ai_config.get_llm()
        
        # Create the deep agent with composite backend
        # Routes /memories/ to persistent store, everything else to ephemeral state
        self.agent = create_deep_agent(
            model=llm,
            system_prompt=self.system_prompt,
            store=self.store,
            backend=lambda rt: CompositeBackend(
                default=StateBackend(rt),
                routes={"/memories/": StoreBackend(rt)}
            )
        )
    
    async def generate_reply(
        self,
        thread_context: str,
        user_persona: Dict[str, Any],
        platform: str,
        user_id: str
    ) -> str:
        """
        Generate a smart reply using the deep agent
        
        Args:
            thread_context: Full email/message thread context
            user_persona: User's communication preferences and style
            platform: Target platform (gmail, slack, calendar)
            user_id: User ID for memory namespace
        
        Returns:
            str: Generated draft reply
        """
        # Construct the prompt with context
        prompt = f"""Generate a draft reply for the following email thread.

Platform: {platform}
User ID: {user_id}

Thread Context:
{thread_context}

User Persona Information:
{self._format_persona(user_persona)}

Please generate an appropriate draft reply that:
1. Addresses all points in the thread
2. Matches the user's communication style
3. Is formatted appropriately for {platform}
4. Maintains the right tone for the relationship

Return only the draft reply text, without any explanations or metadata.
"""
        
        # Invoke the agent
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config={"configurable": {"thread_id": f"reply_{user_id}"}}
        )
        
        # Extract the final message
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "content"):
                return last_message.content
            elif isinstance(last_message, dict):
                return last_message.get("content", "")
        
        return ""
    
    def _format_persona(self, persona: Dict[str, Any]) -> str:
        """Format persona data for the prompt"""
        lines = []
        
        if "style_patterns" in persona:
            lines.append("Communication Style:")
            for key, value in persona["style_patterns"].items():
                lines.append(f"  - {key}: {value}")
        
        if "contacts" in persona:
            lines.append("\nKey Contacts:")
            for contact in persona["contacts"][:5]:  # Limit to top 5
                lines.append(f"  - {contact}")
        
        if "preferences" in persona:
            lines.append("\nPreferences:")
            for key, value in persona["preferences"].items():
                lines.append(f"  - {key}: {value}")
        
        return "\n".join(lines) if lines else "No persona data available"
    
    async def store_observation(
        self,
        user_id: str,
        observation_type: str,
        observation_data: Dict[str, Any]
    ) -> None:
        """
        Store an observation in the user's long-term memory
        
        Args:
            user_id: User ID for memory namespace
            observation_type: Type of observation (style, contact, preference)
            observation_data: The observation data to store
        """
        # Store in the agent's memory system
        memory_path = f"/memories/{observation_type}.txt"
        
        # Format observation as text
        observation_text = self._format_observation(observation_type, observation_data)
        
        # Use the agent to write to memory
        await self.agent.ainvoke(
            {"messages": [{
                "role": "user",
                "content": f"Store this observation in {memory_path}:\n\n{observation_text}"
            }]},
            config={"configurable": {"thread_id": f"memory_{user_id}"}}
        )
    
    def _format_observation(self, obs_type: str, data: Dict[str, Any]) -> str:
        """Format observation data as text"""
        lines = [f"# {obs_type.replace('_', ' ').title()} Observation"]
        lines.append(f"Timestamp: {data.get('timestamp', 'N/A')}")
        lines.append("")
        
        for key, value in data.items():
            if key != "timestamp":
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)


def get_smart_reply_agent(store: Optional[InMemoryStore] = None) -> SmartReplyDeepAgent:
    """
    Get or create a smart reply deep agent instance
    
    Args:
        store: Optional LangGraph Store for long-term memory
    
    Returns:
        SmartReplyDeepAgent: Configured deep agent
    """
    return SmartReplyDeepAgent(store=store)
