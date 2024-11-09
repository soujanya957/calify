import os
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the path to your credentials.json file
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '../config/credentials.json')

# Initialize the Google OAuth 2.0 flow
def google_oauth_flow():
    # Load the credentials from the file
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )
    creds = flow.run_local_server(port=0)
    return creds
