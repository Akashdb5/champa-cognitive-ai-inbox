"""
Google Calendar adapter using Google API Client

This adapter implements the PlatformInterface for Google Calendar, providing
standardized OAuth management and event access.
"""
from typing import List, Optional
from datetime import datetime, timezone
import logging
import asyncio

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
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


class GoogleCalendarAdapter(PlatformInterface):
    """
    Google Calendar platform adapter using Google API Client
    
    Implements the PlatformInterface for Calendar integration with:
    - OAuth 2.0 authentication
    - Event fetching
    - Token refresh
    
    Note: Calendar events are treated as "messages" for unified inbox compatibility
    """
    
    # OAuth scopes for Calendar access
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = None):
        """
        Initialize the Calendar adapter
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri or "http://localhost:8000/api/platforms/calendar/callback"
    
    async def connect(self, user_id: str, auth_code: str) -> Connection:
        """
        Connect a user's Google Calendar using OAuth authorization code
        
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
            
            # Create OAuth flow with redirect_uri (same pattern as Gmail)
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
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            # Exchange authorization code for tokens
            # Note: Don't pass scopes here, they're already in the flow (same as Gmail)
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            return Connection(
                platform="calendar",
                user_id=user_id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expires_at=credentials.expiry
            )
        except Exception as e:
            logger.error(f"Failed to connect Calendar for user {user_id}: {str(e)}")
            raise Exception(f"Calendar connection failed: {str(e)}")
    
    async def disconnect(self, user_id: str) -> None:
        """
        Disconnect a user's Google Calendar
        
        Args:
            user_id: The user's ID in our system
        """
        logger.info(f"Disconnected Calendar for user {user_id}")
    
    async def fetch_messages(self, user_id: str, access_token: str, refresh_token: str,
                            since: Optional[datetime] = None) -> List[RawMessage]:
        """
        Fetch calendar events as messages
        
        Args:
            user_id: The user's ID in our system
            access_token: User's Google access token
            refresh_token: User's Google refresh token
            since: Optional datetime to fetch events after this time
        
        Returns:
            List of RawMessage objects representing calendar events
        
        Raises:
            Exception: If fetching fails
        """
        try:
            # Create credentials
            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            def _fetch_events():
                """Fetch events synchronously"""
                # Build Calendar service
                service = build('calendar', 'v3', credentials=creds)
                
                # Calculate time range
                time_min = since.isoformat() + 'Z' if since else datetime.utcnow().isoformat() + 'Z'
                
                # Fetch events
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=time_min,
                    maxResults=100,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                messages = []
                
                for event in events:
                    # Extract event details
                    event_id = event['id']
                    summary = event.get('summary', 'No title')
                    description = event.get('description', '')
                    location = event.get('location', '')
                    
                    # Get start time
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    
                    # Get end time
                    end = event['end'].get('dateTime', event['end'].get('date'))
                    
                    # Get attendees
                    attendees = event.get('attendees', [])
                    attendee_emails = [a.get('email', '') for a in attendees]
                    
                    # Get organizer
                    organizer = event.get('organizer', {})
                    organizer_email = organizer.get('email', 'unknown')
                    organizer_name = organizer.get('displayName', organizer_email)
                    
                    # Create content
                    content_parts = [summary]
                    if description:
                        content_parts.append(f"\n\n{description}")
                    if location:
                        content_parts.append(f"\n\nLocation: {location}")
                    if attendee_emails:
                        content_parts.append(f"\n\nAttendees: {', '.join(attendee_emails)}")
                    
                    content = ''.join(content_parts)
                    
                    # Create RawMessage
                    messages.append(RawMessage(
                        platform_message_id=event_id,
                        sender=organizer_name,
                        content=content,
                        timestamp=start_dt,
                        subject=summary,
                        thread_id=event_id,
                        metadata={
                            'event_id': event_id,
                            'start': start,
                            'end': end,
                            'location': location,
                            'attendees': attendee_emails,
                            'organizer': organizer_email,
                            'html_link': event.get('htmlLink', ''),
                            'status': event.get('status', 'confirmed')
                        }
                    ))
                
                return messages
            
            # Run in thread pool
            messages = await asyncio.to_thread(_fetch_events)
            
            logger.info(f"Fetched {len(messages)} calendar events for user {user_id}")
            return messages
            
        except HttpError as e:
            logger.error(f"Google Calendar API error for user {user_id}: {str(e)}")
            raise Exception(f"Calendar event fetch failed: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to fetch Calendar events for user {user_id}: {str(e)}")
            raise Exception(f"Calendar event fetch failed: {str(e)}")
    
    async def send_message(self, user_id: str, access_token: str, refresh_token: str,
                          message: OutgoingMessage) -> MessageResult:
        """
        Send a message through Calendar (create/update event)
        
        Note: This is not typically used for Calendar, but included for interface compatibility
        
        Args:
            user_id: The user's ID in our system
            access_token: User's Google access token
            refresh_token: User's Google refresh token
            message: The message to send (event details)
        
        Returns:
            MessageResult indicating success or failure
        """
        return MessageResult(
            success=False,
            error="Calendar does not support sending messages. Use Calendar tools instead."
        )
    
    async def refresh_token(self, user_id: str, refresh_token: str) -> Connection:
        """
        Refresh an expired Google Calendar access token
        
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
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            def _refresh():
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                return creds
            
            # Run blocking call in thread pool
            refreshed_creds = await asyncio.to_thread(_refresh)
            
            # Calculate token expiration
            token_expires_at = None
            if refreshed_creds.expiry:
                token_expires_at = refreshed_creds.expiry
            
            return Connection(
                platform="calendar",
                user_id=user_id,
                access_token=refreshed_creds.token,
                refresh_token=refreshed_creds.refresh_token or refresh_token,
                token_expires_at=token_expires_at,
                redirect_url=None
            )
        except Exception as e:
            logger.error(f"Failed to refresh Calendar token for user {user_id}: {str(e)}")
            raise Exception(f"Calendar token refresh failed: {str(e)}")
    
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
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            state=state,
            prompt='consent'
        )
        
        return auth_url
