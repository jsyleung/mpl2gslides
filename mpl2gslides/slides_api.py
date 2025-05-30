from googleapiclient.discovery import build
import uuid

def get_presentation(service, title, drive_service=None):
    if drive_service is None:
        # Build Drive API service with same credentials
        creds = service._http.credentials
        drive_service = build('drive', 'v3', credentials=creds)

    # Search for presentation with matching title
    results = drive_service.files().list(
        q=f"name='{title}' and mimeType='application/vnd.google-apps.presentation'",
        spaces='drive',
        fields="files(id, name)",
        pageSize=1
    ).execute()

    items = results.get('files', [])
    if items:
        return items[0]['id']  # Existing presentation ID

    # Create new if not found
    presentation = service.presentations().create(body={"title": title}).execute()
    return presentation['presentationId']

def add_blank_slide(service, presentation_id, session_id=None):
    if session_id is None:
        session_id = uuid.uuid4().hex[:6]

    response = service.presentations().get(presentationId=presentation_id).execute()
    slide_id = f"slide_{len(response['slides']) + 1}_{session_id}"
    request = {
        'createSlide': {
            'objectId': slide_id,
            'insertionIndex': '1',
            'slideLayoutReference': {'predefinedLayout': 'BLANK'}
        }
    }
    service.presentations().batchUpdate(
        presentationId=presentation_id, body={'requests': [request]}).execute()
    return slide_id
