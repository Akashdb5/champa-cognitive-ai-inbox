"""
Slack tools for chat agent integration

These tools allow the chat agent to interact with Slack directly:
- List channels
- Get channel history  
- Send messages

Following the project structure: integrations layer provides tools for AI agents.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
import json

from app.models.platform import PlatformConnection
from app.core.config import settings


class SlackToolsManager:
    """Manager for Slack tools that require user context"""
    
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self._connection: Optional[PlatformConnection] = None
    
    def _get_slack_connection(self) -> Optional[PlatformConnection]:
        """Get user's Slack connection"""
        if not self._connection:
            self._connection = self.db.query(PlatformConnection).filter(
                PlatformConnection.user_id == self.user_id,
                PlatformConnection.platform == "slack"
            ).first()
        return self._connection
    
    def list_slack_channels(self) -> str:
        """
        List all Slack channels the user has access to.
        
        Returns:
            JSON string with list of channels (id, name, is_private)
        """
        connection = self._get_slack_connection()
        if not connection:
            return json.dumps({"error": "Slack not connected. Please connect Slack first."})
        
        try:
            from slack_sdk import WebClient
            client = WebClient(token=connection.access_token)
            
            # Get all conversations (channels, DMs, etc.)
            response = client.conversations_list(
                types="public_channel,private_channel",
                limit=100
            )
            
            channels = [
                {
                    "id": channel["id"],
                    "name": channel.get("name", "direct_message"),
                    "is_private": channel.get("is_private", False),
                    "num_members": channel.get("num_members", 0)
                }
                for channel in response.get("channels", [])
            ]
            
            return json.dumps({
                "success": True,
                "channels": channels,
                "count": len(channels)
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to list channels: {str(e)}"})
    
    def get_slack_channel_history(self, channel_id: str, limit: int = 20) -> str:
        """
        Get recent message history from a Slack channel.
        
        Args:
            channel_id: The Slack channel ID (e.g., 'C1234567890') or channel name (e.g., 'general' or '#general')
            limit: Maximum number of messages to fetch (default: 20, max: 100)
        
        Returns:
            JSON string with message history
        """
        connection = self._get_slack_connection()
        if not connection:
            return json.dumps({"error": "Slack not connected. Please connect Slack first."})
        
        try:
            from slack_sdk import WebClient
            client = WebClient(token=connection.access_token)
            
            # If channel_id looks like a name (starts with # or no C prefix), try to find the ID
            if channel_id.startswith('#') or not channel_id.startswith('C'):
                channel_name = channel_id.lstrip('#')
                
                # List channels to find the ID
                channels_response = client.conversations_list(
                    types="public_channel,private_channel",
                    limit=200
                )
                
                for channel in channels_response.get("channels", []):
                    if channel.get("name") == channel_name:
                        channel_id = channel["id"]
                        break
                else:
                    return json.dumps({
                        "error": f"Channel '{channel_name}' not found. Use list_slack_channels to see available channels.",
                        "suggestion": "Try listing channels first with list_slack_channels()"
                    })
            
            # Get channel history
            response = client.conversations_history(
                channel=channel_id,
                limit=min(limit, 100)
            )
            
            messages = []
            for msg in response.get("messages", []):
                # Skip bot messages and system messages
                if msg.get("subtype") in ["bot_message", "channel_join", "channel_leave"]:
                    continue
                
                # Get user info
                user_id = msg.get("user", "unknown")
                user_name = user_id
                try:
                    user_info = client.users_info(user=user_id)
                    user_name = user_info["user"].get("real_name") or user_info["user"].get("name", user_id)
                except:
                    pass
                
                messages.append({
                    "text": msg.get("text", ""),
                    "user": user_name,
                    "timestamp": msg.get("ts", ""),
                    "thread_ts": msg.get("thread_ts"),
                    "reactions": msg.get("reactions", [])
                })
            
            return json.dumps({
                "success": True,
                "channel_id": channel_id,
                "messages": messages,
                "count": len(messages)
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to get channel history: {str(e)}"})
    
    def send_slack_message(self, channel_id: str, text: str, thread_ts: Optional[str] = None) -> str:
        """
        Send a message to a Slack channel.
        
        Args:
            channel_id: The Slack channel ID (e.g., 'C1234567890')
            text: The message text to send
            thread_ts: Optional thread timestamp to reply in a thread
        
        Returns:
            JSON string with send result
        """
        connection = self._get_slack_connection()
        if not connection:
            return json.dumps({"error": "Slack not connected. Please connect Slack first."})
        
        try:
            from slack_sdk import WebClient
            client = WebClient(token=connection.access_token)
            
            # Send message
            response = client.chat_postMessage(
                channel=channel_id,
                text=text,
                thread_ts=thread_ts
            )
            
            return json.dumps({
                "success": True,
                "channel": response["channel"],
                "timestamp": response["ts"],
                "message": "Message sent successfully"
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to send message: {str(e)}"})


def create_slack_tools_for_agent(db: Session, user_id: str) -> List:
    """
    Create LangChain tools for Slack interactions.
    
    This function is called by the chat agent to get Slack tools.
    
    Args:
        db: Database session
        user_id: User ID for accessing their Slack connection
    
    Returns:
        List of LangChain tool functions
    """
    from langchain.tools import tool
    
    manager = SlackToolsManager(db, user_id)
    
    @tool
    def list_slack_channels() -> str:
        """List all Slack channels the user has access to. Returns channel names and IDs."""
        return manager.list_slack_channels()
    
    @tool
    def get_slack_channel_history(channel_id: str, limit: int = 20) -> str:
        """
        Get recent messages from a Slack channel.
        
        Args:
            channel_id: The Slack channel ID (e.g., 'C1234567890')
            limit: Number of messages to fetch (default: 20, max: 100)
        """
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
        return manager.send_slack_message(channel_id, text, thread_ts)
    
    return [
        list_slack_channels,
        get_slack_channel_history,
        send_slack_message
    ]
