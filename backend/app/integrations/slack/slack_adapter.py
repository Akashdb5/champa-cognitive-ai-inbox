"""
Direct Slack integration using Slack SDK

This adapter implements the PlatformInterface for Slack, providing
standardized message fetching, sending, and OAuth management.
"""
from typing import List, Optional
from datetime import datetime, timezone
import logging
import asyncio

from slack_sdk import WebClient
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.errors import SlackApiError

from app.integrations.interfaces import (
    PlatformInterface,
    RawMessage,
    OutgoingMessage,
    MessageResult,
    Connection
)

logger = logging.getLogger(__name__)


class SlackAdapter(PlatformInterface):
    """
    Slack platform adapter using Slack SDK
    
    Implements the PlatformInterface for Slack integration with:
    - OAuth 2.0 authentication
    - Message fetching from channels and DMs
    - Message sending
    - Token refresh
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = None):
        """
        Initialize the Slack adapter
        
        Args:
            client_id: Slack OAuth client ID
            client_secret: Slack OAuth client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri or "http://localhost:8000/api/platforms/slack/callback"
        
        # Slack OAuth scopes needed for reading and sending messages
        self.scopes = [
            'channels:history',
            'channels:read',
            'chat:write',
            'groups:history',
            'groups:read',
            'im:history',
            'im:read',
            'mpim:history',
            'mpim:read',
            'users:read',
            'users:read.email'
        ]
    
    async def connect(self, user_id: str, auth_code: str) -> Connection:
        """
        Connect a user's Slack workspace using OAuth authorization code
        
        Args:
            user_id: The user's ID in our system
            auth_code: OAuth authorization code from Slack
        
        Returns:
            Connection object with access tokens
        
        Raises:
            Exception: If connection fails
        """
        try:
            # Exchange authorization code for access token
            client = WebClient()
            
            def _exchange_code():
                return client.oauth_v2_access(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    code=auth_code,
                    redirect_uri=self.redirect_uri
                )
            
            # Run blocking call in thread pool
            response = await asyncio.to_thread(_exchange_code)
            
            # Extract tokens and metadata
            access_token = response['access_token']
            team_id = response['team']['id']
            user_slack_id = response['authed_user']['id']
            
            # Slack tokens don't expire, but we store metadata
            return Connection(
                platform="slack",
                user_id=user_id,
                access_token=access_token,
                refresh_token=None,  # Slack doesn't use refresh tokens
                token_expires_at=None,  # Slack tokens don't expire
                redirect_url=None
            )
        except SlackApiError as e:
            logger.error(f"Slack API error connecting user {user_id}: {e.response['error']}")
            raise Exception(f"Slack connection failed: {e.response['error']}")
        except Exception as e:
            logger.error(f"Failed to connect Slack for user {user_id}: {str(e)}")
            raise Exception(f"Slack connection failed: {str(e)}")
    
    async def disconnect(self, user_id: str) -> None:
        """
        Disconnect a user's Slack workspace
        
        Args:
            user_id: The user's ID in our system
        
        Note: Slack tokens are revoked by removing the app from the workspace
        """
        logger.info(f"Disconnected Slack for user {user_id}")
    
    async def fetch_messages(self, user_id: str, access_token: str, refresh_token: str,
                            since: Optional[datetime] = None) -> List[RawMessage]:
        """
        Fetch messages from Slack for a user
        
        Args:
            user_id: The user's ID in our system
            access_token: User's Slack access token
            refresh_token: Not used for Slack (kept for interface compatibility)
            since: Optional datetime to fetch messages after this time
        
        Returns:
            List of RawMessage objects from all accessible channels and DMs
        
        Raises:
            Exception: If fetching fails
        """
        try:
            client = WebClient(token=access_token)
            messages = []
            
            # Calculate oldest timestamp for filtering
            oldest = str(since.timestamp()) if since else "0"
            
            def _fetch_conversations_and_messages():
                """Fetch all conversations and their messages synchronously"""
                all_messages = []
                
                # Get list of all conversations (channels, DMs, group DMs)
                conversations = client.conversations_list(
                    types="public_channel,private_channel,mpim,im",
                    limit=100
                )
                
                for conversation in conversations['channels']:
                    channel_id = conversation['id']
                    channel_name = conversation.get('name', 'direct_message')
                    
                    try:
                        # Fetch message history for this conversation
                        history = client.conversations_history(
                            channel=channel_id,
                            oldest=oldest,
                            limit=100
                        )
                        
                        for msg in history.get('messages', []):
                            # Skip bot messages and system messages
                            if msg.get('subtype') in ['bot_message', 'channel_join', 'channel_leave']:
                                continue
                            
                            # Get user info for sender
                            sender_id = msg.get('user', 'unknown')
                            sender_name = sender_id
                            
                            try:
                                user_info = client.users_info(user=sender_id)
                                sender_name = user_info['user'].get('real_name') or user_info['user'].get('name', sender_id)
                            except:
                                pass  # Use sender_id if user info fails
                            
                            # Parse timestamp
                            ts = float(msg.get('ts', '0'))
                            timestamp = datetime.fromtimestamp(ts, tz=timezone.utc)
                            
                            # Extract message text
                            text = msg.get('text', '')
                            
                            # Create RawMessage
                            all_messages.append(RawMessage(
                                platform_message_id=f"{channel_id}_{msg['ts']}",
                                sender=sender_name,
                                content=text,
                                timestamp=timestamp,
                                subject=f"#{channel_name}",  # Use channel name as subject
                                thread_id=msg.get('thread_ts'),  # Thread timestamp if in thread
                                metadata={
                                    'channel_id': channel_id,
                                    'channel_name': channel_name,
                                    'user_id': sender_id,
                                    'ts': msg['ts'],
                                    'type': conversation.get('is_im', False) and 'dm' or 'channel',
                                    'reactions': msg.get('reactions', []),
                                    'attachments': msg.get('attachments', []),
                                    'files': msg.get('files', [])
                                }
                            ))
                    except SlackApiError as e:
                        logger.warning(f"Failed to fetch messages from channel {channel_id}: {e.response['error']}")
                        continue
                
                return all_messages
            
            # Run in thread pool
            messages = await asyncio.to_thread(_fetch_conversations_and_messages)
            
            logger.info(f"Fetched {len(messages)} messages from Slack for user {user_id}")
            return messages
            
        except SlackApiError as e:
            logger.error(f"Slack API error for user {user_id}: {e.response['error']}")
            raise Exception(f"Slack message fetch failed: {e.response['error']}")
        except Exception as e:
            logger.error(f"Failed to fetch Slack messages for user {user_id}: {str(e)}")
            raise Exception(f"Slack message fetch failed: {str(e)}")
    
    async def send_message(self, user_id: str, access_token: str, refresh_token: str,
                          message: OutgoingMessage) -> MessageResult:
        """
        Send a message through Slack
        
        Args:
            user_id: The user's ID in our system
            access_token: User's Slack access token
            refresh_token: Not used for Slack (kept for interface compatibility)
            message: The message to send
                - recipient: Channel ID or user ID
                - content: Message text
                - thread_id: Optional thread timestamp for threaded replies
        
        Returns:
            MessageResult indicating success or failure
        """
        try:
            client = WebClient(token=access_token)
            
            def _send():
                return client.chat_postMessage(
                    channel=message.recipient,
                    text=message.content,
                    thread_ts=message.thread_id  # Reply in thread if provided
                )
            
            # Run in thread pool
            response = await asyncio.to_thread(_send)
            
            logger.info(f"Sent Slack message for user {user_id}")
            return MessageResult(
                success=True,
                platform_message_id=f"{response['channel']}_{response['ts']}"
            )
            
        except SlackApiError as e:
            logger.error(f"Slack API error for user {user_id}: {e.response['error']}")
            return MessageResult(
                success=False,
                error=e.response['error']
            )
        except Exception as e:
            logger.error(f"Failed to send Slack message for user {user_id}: {str(e)}")
            return MessageResult(
                success=False,
                error=str(e)
            )
    
    async def refresh_token(self, user_id: str, refresh_token: str) -> Connection:
        """
        Refresh an expired Slack access token
        
        Note: Slack tokens don't expire, so this is a no-op
        
        Args:
            user_id: The user's ID in our system
            refresh_token: Not used for Slack
        
        Returns:
            Connection object (unchanged)
        
        Raises:
            Exception: If called (Slack tokens don't need refresh)
        """
        raise Exception("Slack tokens do not expire and cannot be refreshed")
    
    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """
        Get OAuth authorization URL for user to visit
        
        Args:
            redirect_uri: Where to redirect after authorization
            state: State parameter for CSRF protection
        
        Returns:
            Authorization URL
        """
        authorize_url_generator = AuthorizeUrlGenerator(
            client_id=self.client_id,
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        
        return authorize_url_generator.generate(state=state)
