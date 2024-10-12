# hackpsufrom google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
import os

def get_google_calendar_events():
    """Fetches events from the Google Calendar"""
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    """Check if valid credentials exist in Google accounts"""
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('/Users/kmjason/Desktop/HACK_PSU-2024/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        """Save credentials for next run"""
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []
        
        # Print the events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start}: {event['summary']}")
        
        return events

    except Exception as e:
        print(f'An error occurred: {e}')
        return None


if __name__ == '__main__':
    get_google_calendar_events()
