from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import json
from datetime import datetime, timedelta
from django.conf import settings

class GoogleCalendarAPI:
    def __init__(self):
        self.creds = None
        self.service = None
        self.credentials_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH
        self.token_path = settings.GOOGLE_CALENDAR_TOKEN_PATH
        self.scopes = settings.GOOGLE_CALENDAR_SETTINGS['scopes']
        self.initialize_credentials()

    def initialize_credentials(self):
        """Initialize Google Calendar credentials"""
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google Calendar credentials not found at {self.credentials_path}. "
                        "Please download the credentials file from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for future use
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    def schedule_automation(self, task_data):
        """Schedule an automation task in Google Calendar"""
        if not self.service:
            self.initialize_credentials()

        start_time = task_data['start_time']
        end_time = start_time + timedelta(minutes=30)  # Default 30min duration

        event = {
            'summary': f"Social Media Automation - {task_data['platform']}",
            'description': json.dumps({
                'platform': task_data['platform'],
                'action': task_data['action'],
                'target_url': task_data['target_url'],
                'quantity': task_data['quantity'],
                'task_id': str(task_data['task_id'])
            }),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'reminders': {
                'useDefault': True
            }
        }

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return event.get('id')
        except Exception as e:
            print(f"Failed to schedule event: {str(e)}")
            return None

    def get_upcoming_tasks(self):
        """Get all upcoming automation tasks"""
        if not self.service:
            self.initialize_credentials()

        now = datetime.utcnow().isoformat() + 'Z'
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except Exception as e:
            print(f"Failed to get upcoming tasks: {str(e)}")
            return []

    def cancel_task(self, event_id):
        """Cancel a scheduled automation task"""
        if not self.service:
            self.initialize_credentials()

        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except Exception as e:
            print(f"Failed to cancel task: {str(e)}")
            return False 