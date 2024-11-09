from google_auth_oauthlib.flow import Flow
from flask import session, redirect, url_for
import os

def start_oauth_flow():
    flow = Flow.from_client_secrets_file(
        'credentials.json',  # Path to your Google OAuth credentials
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI")
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

def get_oauth_tokens(code):
    flow = Flow.from_client_secrets_file(
        'credentials.json', 
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI")
    )
    flow.fetch_token(authorization_response=code)
    credentials = flow.credentials
    session['credentials'] = credentials
    return credentials
