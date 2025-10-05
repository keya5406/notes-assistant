import os
import io
import pickle
from typing import List, Dict
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Drive API scope: read-only access
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

TOKEN_PATH = "token.pickle"
BASE_DIR = Path(__file__).parent
CREDENTIALS_PATH = BASE_DIR / "secrets" / "credentials.json"

def get_drive_service():
    """Authenticate and return Google Drive API service."""
    creds = None

    # Load saved token if available
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # If no valid creds, login manually
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)

def list_files_in_folder(folder_id: str) -> List[Dict]:
    """Recursively list all PDF files in a given Google Drive folder (including subfolders)."""
    service = get_drive_service()
    all_files = []

    def _list_recursive(fid):
        results = service.files().list(
            q=f" '{fid}' in parents and (mimeType='application/pdf' or mimeType='application/vnd.google-apps.folder')",
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        files = results.get("files", [])
        for f in files:
            if f["mimeType"] == "application/vnd.google-apps.folder":
                # Recursive call for subfolder
                _list_recursive(f["id"])
            elif f["mimeType"] == "application/pdf":
                all_files.append(f)

    _list_recursive(folder_id)
    return all_files

def download_file(file_id: str) -> bytes:
    """Download a file from Google Drive as bytes."""
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    buffer.seek(0)
    return buffer.read()
