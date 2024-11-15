from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os
from calendar_utils import parse_event, create_event_in_calendar

# App Setup
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with a secure key in production
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For local testing only

# Google OAuth 2.0 Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = 'client_secret.json'

# Routes
@app.route("/login")
def login():
    """Starts the OAuth 2.0 authorization flow."""
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES
    )
    flow.redirect_uri = url_for("callback", _external=True)
    
    # Generate the authorization URL
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    
    # Store state in session to verify on callback
    session["state"] = state
    return redirect(authorization_url)


# hello

@app.route("/callback")
def callback():
    """Handles OAuth callback, stores user credentials."""
    state = session["state"]
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = url_for("callback", _external=True)
    
    # Get authorization response from the request URL
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    # Store credentials in the session
    credentials = flow.credentials
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    
    flash("Successfully logged in!")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    """Logs the user out by clearing credentials from session."""
    session.pop("credentials", None)
    flash("You have been logged out.")
    return redirect(url_for("index"))
@app.route("/", methods=["GET", "POST"])
def index():
    """Main page to interact with Google Calendar."""
    if "credentials" not in session:
        return redirect(url_for("login"))
    service = get_calendar_service()

    if request.method == "POST":
        prompt = request.form.get("prompt")
        print("Debug - Received prompt:", prompt)  
        event_data = parse_event(prompt)
        session["event_data"] = event_data
        # Render the confirmation page with parsed event details
        return render_template("confirm.html", event_data=event_data)

    return render_template("index.html")

def get_calendar_service():
    """Initializes the Google Calendar service using stored credentials."""
    if "credentials" not in session:
        raise Exception("User is not logged in.")
    
    credentials = google.oauth2.credentials.Credentials(**session["credentials"])
    service = googleapiclient.discovery.build("calendar", "v3", credentials=credentials)
    return service

@app.route('/confirm', methods=['GET','POST'])
def confirm():
    # Retrieve the prompt from the POST request
    event_data = session.get('event_data')
    service = get_calendar_service()  # Initialize Google Calendar service

    # Parse the prompt for structured event details

    # Check if parsed event data is valid and call create_event_in_calendar
    if event_data:
        create_event_in_calendar(service, event_data)  # Create event using parsed data

    # Optionally, you can print a success message for manual confirmation
    session.pop('event_data', None)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)