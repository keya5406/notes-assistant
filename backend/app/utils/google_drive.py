import os
import io
import pickle
import base64
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

# Google Drive API scope: read-only access
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    """
    Authenticate using OAuth token stored in environment variable (Base64 of token.pickle).
    """
    token_b64 = os.environ.get("GOOGLE_DRIVE_TOKEN")
    if not token_b64:
        raise ValueError("Missing GOOGLE_DRIVE_TOKEN environment variable")

    # Decode Base64 to bytes and load as pickle
    token_bytes = base64.b64decode(token_b64)
    creds = pickle.load(io.BytesIO(token_bytes))

    # Refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("drive", "v3", credentials=creds)


def list_files_in_folder(folder_id: str) -> List[Dict]:
    """Recursively list all PDF files in a folder."""
    service = get_drive_service()
    all_files = []

    def _list_recursive(fid):
        results = service.files().list(
            q=f"'{fid}' in parents and (mimeType='application/pdf' or mimeType='application/vnd.google-apps.folder')",
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()

        for f in results.get("files", []):
            if f["mimeType"] == "application/vnd.google-apps.folder":
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
