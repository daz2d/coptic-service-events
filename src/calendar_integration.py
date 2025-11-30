"""Google Calendar integration"""

import logging
import os
from datetime import datetime
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


class GoogleCalendarIntegration:
    """Handles Google Calendar API integration"""
    
    def __init__(self, config):
        self.config = config
        self.service = None
        self.calendar_id = None
        
        if config.get('google_calendar.enabled'):
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar API service"""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = None
            token_path = Path('token.json')
            credentials_path = Path('credentials.json')
            
            # Load existing credentials
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not credentials_path.exists():
                        logger.warning("credentials.json not found. Google Calendar disabled.")
                        logger.warning("See docs/google_calendar_setup.md for setup instructions")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            self._setup_calendar()
            
            logger.info("Google Calendar integration initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Google Calendar: {e}")
            logger.warning("Google Calendar integration disabled")
    
    def _setup_calendar(self):
        """Create or find the Coptic Events calendar"""
        try:
            calendar_name = self.config.get('google_calendar.calendar_name', 
                                           'Coptic Service Events')
            
            # List existing calendars
            calendar_list = self.service.calendarList().list().execute()
            
            for calendar in calendar_list.get('items', []):
                if calendar['summary'] == calendar_name:
                    self.calendar_id = calendar['id']
                    logger.info(f"Using existing calendar: {calendar_name}")
                    return
            
            # Create new calendar
            calendar = {
                'summary': calendar_name,
                'description': 'Service and volunteer events from Coptic Orthodox churches',
                'timeZone': 'America/New_York'
            }
            
            created_calendar = self.service.calendars().insert(body=calendar).execute()
            self.calendar_id = created_calendar['id']
            logger.info(f"Created new calendar: {calendar_name}")
            
        except Exception as e:
            logger.error(f"Error setting up calendar: {e}")
    
    def add_events(self, events: List[dict]) -> int:
        """Add events to Google Calendar"""
        if not self.service or not self.calendar_id:
            logger.warning("Google Calendar not initialized")
            return 0
        
        added_count = 0
        
        for event in events:
            try:
                calendar_event = event.to_calendar_event() if hasattr(event, 'to_calendar_event') else event
                
                # Add custom reminders from config
                reminder_minutes = self.config.get('google_calendar.reminder_minutes', [1440, 60])
                calendar_event['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': minutes} 
                        for minutes in reminder_minutes
                    ]
                }
                
                created_event = self.service.events().insert(
                    calendarId=self.calendar_id,
                    body=calendar_event
                ).execute()
                
                logger.info(f"Added event to calendar: {calendar_event['summary']}")
                added_count += 1
                
            except Exception as e:
                logger.error(f"Error adding event to calendar: {e}")
        
        return added_count
    
    def remove_event(self, event_id: str):
        """Remove event from Google Calendar"""
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            logger.info(f"Removed event from calendar: {event_id}")
        except Exception as e:
            logger.error(f"Error removing event: {e}")
