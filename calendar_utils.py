import re
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

import re

def parse_event(prompt):
    """
    Parse natural language input to detect the operation type and extract event details.
    Returns a dictionary with operation type and event details.
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Input must be a non-empty string")

    # Define operation keywords and corresponding regex patterns
    operation_keywords = {
        'create': r'\bcreate\b',
        'delete': r'\bdelete\b',
        'list': r'\blist\b',
    }

    # Initialize operation type as None
    operation_type = None

    # Check for the operation keyword in the prompt
    for op, keyword in operation_keywords.items():
        if re.search(keyword, prompt, re.IGNORECASE):
            operation_type = op
            break
    
    if operation_type is None:
        raise ValueError("No valid operation found in the input.")

    # Regex pattern to capture event data for create, delete, or list operations
    pattern = r"""
    (?P<title>.*?)                                     # Event title/summary (required)
    (?:\s+on\s+(?P<date>\d{4}-\d{2}-\d{2}))?           # Date (optional) in YYYY-MM-DD format
    (?:\s+from\s+(?P<start_time>\d{1,2}:\d{2}\s*(?:AM|PM)))?  # Start time (optional)
    (?:\s+to\s+(?P<end_time>\d{1,2}:\d{2}\s*(?:AM|PM)))?      # End time (optional)
    (?:\s+at\s+(?P<location>[^,]+))?                    # Location (optional)
    (?:\s+with\s+(?P<attendees>[\w\s@.,]+?))?          # Attendees (optional)
    (?:\s+description:?\s+(?P<description>.+))?         # Description (optional)
    \s*$                                                # End of string
    """.strip()
    
    pattern_compiled = re.compile(pattern, re.VERBOSE | re.IGNORECASE)
    match = pattern_compiled.match(prompt.strip())

    event_data = {}

    if operation_type == 'create' and match:
        event_data = match.groupdict()
        event = {
            'title': event_data['title'].strip(),
            'start': None,
            'end': None,
            'date': event_data['date'],
            'location': event_data['location'] if event_data['location'] else None,
            'attendees': event_data['attendees'].split(',') if event_data['attendees'] else [],
            'description': event_data['description'] if event_data['description'] else None
        }
        
        
        # Parse and clean up times if present
        if event_data['start_time']:
            event['start'] = event_data['start_time'].upper().replace(' ', '')
        if event_data['end_time']:
            event['end'] = event_data['end_time'].upper().replace(' ', '')

        return {
            'operation': 'create',
            'event': event
        }
    
    elif operation_type == 'delete':
        # For delete operation, just extract title and date
        event_data = match.groupdict() if match else {}
        return {
            'operation': 'delete',
            'event': {
                'title': event_data.get('title'),
                'date': event_data.get('date')
            }
        }
    
    elif operation_type == 'list':
        # For list operation, no event details needed
        return {
            'operation': 'list',
            'event': None
        }

    else:
        raise ValueError("Invalid input or unsupported operation.")


def create_event_in_calendar(service, event_data, timezone='America/New_York'):
    """
    Creates an event in Google Calendar using the provided data.
    Converts date and time strings to proper ISO format for Google Calendar API.
    Supports both New York and Los Angeles timezones.
    
    Args:
        service: Google Calendar API service instance
        event_data (dict): Dictionary containing event information
        timezone (str): Timezone for the event (default: 'America/New_York')
        
    Returns:
        dict: Created event object or None if error occurs
    """
    event = event_data.get('event')
    print("Creating event:", event)
    # Get date and time info from event
    date = event.get('date')
    start_time = event.get('start')
    end_time = event.get('end')
    
    # Dictionary of supported timezones
    timezones = {
        'America/New_York': 'US/Eastern',
        'America/Los_Angeles': 'US/Pacific'
    }
    
    # If no time provided, default to all-day event
    if not start_time or not end_time:
        cal_event = {
            'summary': event.get('title')[6:],
            'location': event.get('location'),
            'description': event.get('description'),
            'start': {
                'date': date,
                'timeZone': timezone,
            },
            'end': {
                'date': date,
                'timeZone': timezone,
            }
        }
    else:
        try:
            # Convert date and time strings to datetime objects
            start_datetime = datetime.strptime(f'{date} {start_time}', '%Y-%m-%d %I:%M%p')
            end_datetime = datetime.strptime(f'{date} {end_time}', '%Y-%m-%d %I:%M%p')
            
            # Create timezone aware datetimes
            from datetime import timezone as tz
            from zoneinfo import ZoneInfo
            
            # Convert to timezone-aware datetime
            start_datetime = start_datetime.replace(tzinfo=ZoneInfo(timezone))
            end_datetime = end_datetime.replace(tzinfo=ZoneInfo(timezone))
            
            # Convert to ISO format string that Google Calendar API expects
            start_iso = start_datetime.isoformat()
            end_iso = end_datetime.isoformat()
            
            cal_event = {
                'summary': event.get('title')[6:],
                'location': event.get('location'),
                'description': event.get('description'),
                'start': {
                    'dateTime': start_iso,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_iso,
                    'timeZone': timezone,
                }
            }
        except ValueError as e:
            raise ValueError(f"Error parsing date and time: {str(e)}")
    
    # Add optional attendees if present
    if event.get('attendees'):
        cal_event['attendees'] = [{'email': attendee.strip()} for attendee in event.get('attendees')]
    
    # Add default reminders
    cal_event['reminders'] = {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
    }

    print("Creating event:", cal_event)
    
    try:
        created_event = service.events().insert(calendarId='primary', body=cal_event,sendUpdates="all").execute()
        print(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None