"""
Direct Gmail integration using Google Gmail API
"""
from typing import List, Optional
from datetime import datetime
import logging
import base64
import json
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.integrations.interfaces import (
    PlatformInterface,
    RawMessage,
    OutgoingMessage,
    MessageResult,
    Connection
)

logger = logging.getLogger(__name__)


class GoogleGmailAdapter(PlatformInterface):
    """
    Gmail platform adapter using Google Gmail API directly
    
    Implements the PlatformInterface for Gmail integration.
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = None):
        """
        Initialize the Gmail adapter
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri or "http://localhost:8000/api/platforms/gmail/callback"
        # Use only Gmail scopes
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
    
    async def connect(self, user_id: str, auth_code: str) -> Connection:
        """
        Connect a user's Gmail account using OAuth authorization code
        
        Args:
            user_id: The user's ID in our system
            auth_code: OAuth authorization code from Google
        
        Returns:
            Connection object with access tokens
        
        Raises:
            Exception: If connection fails
        """
        try:
            from google_auth_oauthlib.flow import Flow
            
            # Create OAuth flow with redirect_uri
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            # Exchange authorization code for tokens
            # Note: Don't pass scopes here, they're already in the flow
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            return Connection(
                platform="gmail",
                user_id=user_id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expires_at=credentials.expiry
            )
        except Exception as e:
            logger.error(f"Failed to connect Gmail for user {user_id}: {str(e)}")
            raise Exception(f"Gmail connection failed: {str(e)}")
    
    async def disconnect(self, user_id: str) -> None:
        """
        Disconnect a user's Gmail account
        
        Args:
            user_id: The user's ID in our system
        """
        # For Gmail, we just remove the stored credentials
        # The tokens will expire naturally
        logger.info(f"Disconnected Gmail for user {user_id}")
    
    async def fetch_messages(self, user_id: str, access_token: str, refresh_token: str, 
                            since: Optional[datetime] = None) -> List[RawMessage]:
        """
        Fetch messages from Gmail for a user
        
        Args:
            user_id: The user's ID in our system
            access_token: User's Gmail access token
            refresh_token: User's Gmail refresh token
            since: Optional datetime to fetch messages after this time
        
        Returns:
            List of RawMessage objects
        
        Raises:
            Exception: If fetching fails
        """
        import asyncio
        
        def _fetch_sync():
            """Synchronous fetch to run in thread pool"""
            # Create credentials
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )
            
            # Refresh if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            return service, credentials
        
        try:
            # Run blocking calls in thread pool
            service, credentials = await asyncio.to_thread(_fetch_sync)
            
            # Build query
            query = "in:inbox"
            if since:
                query += f" after:{int(since.timestamp())}"
            
            def _list_and_fetch_messages():
                """Fetch messages synchronously in thread pool"""
                # List messages
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=50
                ).execute()
                
                messages = []
                for msg_data in results.get('messages', []):
                    # Get full message
                    msg = service.users().messages().get(
                        userId='me',
                        id=msg_data['id'],
                        format='full'
                    ).execute()
                    
                    # Extract headers
                    headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
                    
                    # Extract body
                    body = self._extract_body(msg['payload'])
                    
                    # Parse timestamp
                    timestamp = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
                    
                    messages.append(RawMessage(
                        platform_message_id=msg['id'],
                        sender=headers.get('From', ''),
                        content=body,
                        timestamp=timestamp,
                        subject=headers.get('Subject'),
                        thread_id=msg.get('threadId'),
                        metadata={
                            'labels': msg.get('labelIds', []),
                            'snippet': msg.get('snippet', ''),
                            'to': headers.get('To', ''),
                            'cc': headers.get('Cc', ''),
                        }
                    ))
                return messages
            
            # Run in thread pool
            messages = await asyncio.to_thread(_list_and_fetch_messages)
            
            logger.info(f"Fetched {len(messages)} messages from Gmail for user {user_id}")
            return messages
            
        except HttpError as e:
            logger.error(f"Gmail API error for user {user_id}: {str(e)}")
            raise Exception(f"Gmail message fetch failed: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to fetch Gmail messages for user {user_id}: {str(e)}")
            raise Exception(f"Gmail message fetch failed: {str(e)}")
    
    async def send_message(self, user_id: str, access_token: str, refresh_token: str,
                          message: OutgoingMessage) -> MessageResult:
        """
        Send an email through Gmail
        
        Args:
            user_id: The user's ID in our system
            access_token: User's Gmail access token
            refresh_token: User's Gmail refresh token
            message: The message to send
        
        Returns:
            MessageResult indicating success or failure
        """
        try:
            # Create credentials
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )
            
            # Refresh if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            
            # Create email
            email_message = MIMEText(message.content)
            email_message['to'] = message.recipient
            email_message['subject'] = message.subject or ''
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
            
            # Send message
            send_params = {'raw': raw_message}
            if message.thread_id:
                send_params['threadId'] = message.thread_id
            
            result = service.users().messages().send(
                userId='me',
                body=send_params
            ).execute()
            
            logger.info(f"Sent email via Gmail for user {user_id}")
            return MessageResult(
                success=True,
                platform_message_id=result['id']
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error for user {user_id}: {str(e)}")
            return MessageResult(
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Failed to send Gmail message for user {user_id}: {str(e)}")
            return MessageResult(
                success=False,
                error=str(e)
            )
    
    async def refresh_token(self, user_id: str, refresh_token: str) -> Connection:
        """
        Refresh an expired Gmail access token
        
        Args:
            user_id: The user's ID in our system
            refresh_token: The refresh token
        
        Returns:
            Updated Connection object with new tokens
        
        Raises:
            Exception: If refresh fails
        """
        try:
            # Create credentials with refresh token
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )
            
            # Refresh
            credentials.refresh(Request())
            
            return Connection(
                platform="gmail",
                user_id=user_id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expires_at=credentials.expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to refresh Gmail token for user {user_id}: {str(e)}")
            raise Exception(f"Gmail token refresh failed: {str(e)}")
    
    def _extract_body(self, payload: dict) -> str:
        """
        Extract email body from Gmail payload
        
        Args:
            payload: Gmail message payload
        
        Returns:
            Email body text
        """
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
                    # Fallback to HTML if no plain text
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
        
        return ""
    
    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """
        Get OAuth authorization URL for user to visit
        
        Args:
            redirect_uri: Where to redirect after authorization
            state: State parameter for CSRF protection
        
        Returns:
            Authorization URL
        """
        from google_auth_oauthlib.flow import Flow
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            state=state,
            prompt='consent'
        )
        
        return auth_url
