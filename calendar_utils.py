import re
from googleapiclient.errors import HttpError

def parse_event(prompt):
    """
    Parse the natural language input to extract event details.
    This can be expanded to use more sophisticated NLP methods.
    """
    # Simple regex pattern for basic parsing (expandable)
    pattern = r"(?P<title>.+?)\s*(at|on)\s*(?P<time>\d{1,2}(:\d{2})?\s*(am|pm)?)\s*(at\s*(?P<location>.+))?"
    match = re.search(pattern, prompt, re.IGNORECASE)

    if match:
        event_data = match.groupdict()
        return event_data
    else:
        return {}

def create_event_in_calendar(service, event_data):
    """
    Creates an event in Google Calendar using the provided data.
    """
    try:
        event = {
            'summary': event_data.get('title'),
            'location': event_data.get('location'),
            'start': {
                'dateTime': event_data.get('time'),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': event_data.get('time'),
                'timeZone': 'America/New_York',
            },
        }
        
        # Insert the event in Google Calendar
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event
    except HttpError as error:
        print(f"An error occurred: {error}")
