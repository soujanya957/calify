from backend.config import googleAuth
from flask import request, jsonify
from services.calendarService import get_free_slots
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

def fetch_calendar_data():
    credentials = session.get('credentials')
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    service = build('calendar', 'v3', credentials=credentials)
    events = service.events().list(calendarId='primary').execute()
    return events.get('items', [])

def get_user_free_slots():
    events = fetch_calendar_data()
    free_slots = get_free_slots(events)
    return jsonify(free_slots)

def get_user_calendar_events(start_time, end_time):
    """
    Retrieves a list of events from the user's Google Calendar within the specified time range.

    Args:
        start_time (str): The start of the time range in ISO 8601 format (e.g., '2023-10-01T00:00:00Z').
        end_time (str): The end of the time range in ISO 8601 format (e.g., '2023-10-07T23:59:59Z').

    Returns:
        list: A list of events, each represented as a dictionary with 'start', 'end', 'summary', 'location', and 'attendees' fields.
    """
    # Authenticate and get credentials
    creds = googleAuth.google_oauth_flow()  
    service = build("calendar", "v3", credentials=creds)

    try:
        # Call the Calendar API to get events
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        # Process events
        if not events:
            print("No upcoming events found.")
            return []

        user_events = []
        for event in events:
            event_info = {
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "summary": event.get("summary"),
                "location": event.get("location"),
                "attendees": [att.get("email") for att in event.get("attendees", [])],
                "id": event.get("id")
            }
            user_events.append(event_info)

        return sorted(user_events, key=lambda x: x["start"])

    except Exception as error:
        print(f"An error occurred: {error}")
        return []
    
def deleteEvent(id):
    creds = googleAuth.google_oauth_flow()  
    service = build("calendar", "v3", credentials=creds)
    try:
        service.events().delete(calendarId='primary', eventId=id,sendNotifications=True).execute()
        return jsonify({"message": "Event deleted successfully."})
    except Exception as error:
        print(f"An error occurred: {error}")
        return jsonify({"message": "An error occurred while deleting the event."})