"""
Google Calendar tools for chat agent integration

These tools allow the chat agent to interact with Google Calendar:
- List events
- Create events
- Update events
- Delete events

Following the project structure: integrations layer provides tools for AI agents.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.models.platform import PlatformConnection
from app.core.config import settings


class CalendarToolsManager:
    """Manager for Google Calendar tools that require user context"""
    
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self._connection: Optional[PlatformConnection] = None
    
    def _get_calendar_connection(self) -> Optional[PlatformConnection]:
        """Get user's Google Calendar connection"""
        if not self._connection:
            self._connection = self.db.query(PlatformConnection).filter(
                PlatformConnection.user_id == self.user_id,
                PlatformConnection.platform == "calendar"
            ).first()
        return self._connection
    
    def _get_calendar_service(self):
        """Get authenticated Google Calendar service"""
        connection = self._get_calendar_connection()
        if not connection:
            return None
        
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            # Create credentials from stored tokens
            creds = Credentials(
                token=connection.access_token,
                refresh_token=connection.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
            
            # Build the service
            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            return None
    
    def list_events(self, limit: int = 10, date_from: Optional[str] = None) -> str:
        """
        List events from the user's primary calendar.
        
        Args:
            limit: Number of events to return (default: 10)
            date_from: Start date to return events from in ISO format (default: today)
        
        Returns:
            JSON string with list of events
        """
        service = self._get_calendar_service()
        if not service:
            return json.dumps({"error": "Google Calendar not connected. Please connect Google Calendar first."})
        
        try:
            # Set default date_from to now if not provided
            if date_from is None:
                date_from = datetime.utcnow().isoformat() + 'Z'
            elif isinstance(date_from, str):
                # Ensure proper ISO format with Z suffix
                if not date_from.endswith('Z'):
                    date_from = datetime.fromisoformat(date_from).isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = service.events().list(
                calendarId='primary',
                timeMin=date_from,
                maxResults=limit,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return json.dumps({"message": "No upcoming events found.", "events": []})
            
            # Format events for response
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'start': start,
                    'end': end,
                    'attendees': [a.get('email') for a in event.get('attendees', [])],
                    'htmlLink': event.get('htmlLink', '')
                })
            
            return json.dumps({
                "success": True,
                "events": formatted_events,
                "count": len(formatted_events)
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to list events: {str(e)}"})
    
    def create_event(
        self,
        start_datetime: str,
        end_datetime: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> str:
        """
        Create a new event in the user's primary calendar.
        
        Args:
            start_datetime: Start date and time in ISO format
            end_datetime: End date and time in ISO format
            title: Title of the event
            description: Detailed description of the event
            location: Location of the event
            timezone: Timezone (default: UTC)
            attendees: List of attendee email addresses
        
        Returns:
            JSON string with created event details
        """
        service = self._get_calendar_service()
        if not service:
            return json.dumps({"error": "Google Calendar not connected. Please connect Google Calendar first."})
        
        try:
            # Format attendees
            attendees_list = [{"email": email} for email in (attendees or [])]
            
            # Parse and format datetime strings
            start_time = datetime.fromisoformat(start_datetime).strftime("%Y-%m-%dT%H:%M:%S")
            end_time = datetime.fromisoformat(end_datetime).strftime("%Y-%m-%dT%H:%M:%S")
            
            # Default timezone to UTC if not provided
            if not timezone:
                timezone = 'UTC'
            
            # Build event object
            event = {
                'summary': title or 'New Event',
                'location': location or '',
                'description': description or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': timezone,
                },
                'attendees': attendees_list,
            }
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return json.dumps({
                "success": True,
                "event_id": created_event['id'],
                "summary": created_event.get('summary'),
                "start": created_event['start'].get('dateTime', created_event['start'].get('date')),
                "end": created_event['end'].get('dateTime', created_event['end'].get('date')),
                "htmlLink": created_event.get('htmlLink'),
                "message": "Event created successfully"
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to create event: {str(e)}"})
    
    def update_event(
        self,
        event_id: str,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> str:
        """
        Update an existing event in the user's primary calendar.
        
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
        service = self._get_calendar_service()
        if not service:
            return json.dumps({"error": "Google Calendar not connected. Please connect Google Calendar first."})
        
        try:
            # Get the existing event
            event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields if provided
            if title is not None:
                event['summary'] = title
            
            if description is not None:
                event['description'] = description
            
            if location is not None:
                event['location'] = location
            
            if start_datetime is not None:
                start_time = datetime.fromisoformat(start_datetime).strftime("%Y-%m-%dT%H:%M:%S")
                event['start'] = {
                    'dateTime': start_time,
                    'timeZone': timezone or event['start'].get('timeZone', 'UTC'),
                }
            
            if end_datetime is not None:
                end_time = datetime.fromisoformat(end_datetime).strftime("%Y-%m-%dT%H:%M:%S")
                event['end'] = {
                    'dateTime': end_time,
                    'timeZone': timezone or event['end'].get('timeZone', 'UTC'),
                }
            
            if attendees is not None:
                event['attendees'] = [{"email": email} for email in attendees]
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return json.dumps({
                "success": True,
                "event_id": updated_event['id'],
                "summary": updated_event.get('summary'),
                "start": updated_event['start'].get('dateTime', updated_event['start'].get('date')),
                "end": updated_event['end'].get('dateTime', updated_event['end'].get('date')),
                "htmlLink": updated_event.get('htmlLink'),
                "message": "Event updated successfully"
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to update event: {str(e)}"})
    
    def delete_event(self, event_id: str) -> str:
        """
        Delete an event from the user's primary calendar.
        
        Args:
            event_id: The Google Calendar event ID
        
        Returns:
            JSON string with deletion result
        """
        service = self._get_calendar_service()
        if not service:
            return json.dumps({"error": "Google Calendar not connected. Please connect Google Calendar first."})
        
        try:
            # Delete the event
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return json.dumps({
                "success": True,
                "event_id": event_id,
                "message": "Event deleted successfully"
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to delete event: {str(e)}"})


def create_calendar_tools_for_agent(db: Session, user_id: str) -> List:
    """
    Create LangChain tools for Google Calendar interactions.
    
    This function is called by the chat agent to get Calendar tools.
    
    Args:
        db: Database session
        user_id: User ID for accessing their Calendar connection
    
    Returns:
        List of LangChain tool functions
    """
    from langchain.tools import tool
    
    manager = CalendarToolsManager(db, user_id)
    
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
        return manager.delete_event(event_id)
    
    return [
        list_calendar_events,
        create_calendar_event,
        update_calendar_event,
        delete_calendar_event
    ]
