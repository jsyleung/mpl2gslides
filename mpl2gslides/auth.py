from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive'
]

def get_slides_service(credentials_path=None, token_path=None, scopes=None):
    if scopes is None:
        scopes = DEFAULT_SCOPES

    if credentials_path is None:
        credentials_path = os.getenv("GSLIDES_CREDENTIALS", "credentials.json")
    if token_path is None:
        token_path = os.getenv("GSLIDES_TOKEN", "token.json")

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Google API credentials file not found at: {credentials_path}")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('slides', 'v1', credentials=creds)
