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

