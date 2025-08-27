import json
import os
from dotenv import load_dotenv
from pathlib import Path

import app.utils.google_drive as google_drive
import app.services.extractor as ext

BASE_DIR = Path(__file__).parent.parent
PROCESSED_FILE_PATH = BASE_DIR / "db" / "processed_files.json"

load_dotenv()
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

def load_processed_files():
    if PROCESSED_FILE_PATH.exists():
        with open(PROCESSED_FILE_PATH, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_files(processed_files):
    with open(PROCESSED_FILE_PATH, "w") as f:
        json.dump(list(processed_files), f)

def sync_drive_folder():
    """Check Google Drive folder for new files, process them."""
    if not DRIVE_FOLDER_ID:
        raise ValueError("DRIVE_FOLDER_ID not set in environment variables")

    processed_files = load_processed_files()
    new_files = google_drive.list_files_in_folder(DRIVE_FOLDER_ID)

    for file in new_files:
        file_id = file["id"]
        file_name = file["name"]

        if file_id in processed_files:
            print(f"Skipping already processed file: {file_name}")
            continue

        print(f"Downloading new file: {file_name}")
        file_bytes = google_drive.download_file(file_id)

        print(f"📄 Extracting text from: {file_name}")
        extracted_text = ext.extract_text_from_pdf_bytes(file_bytes)

        print(extracted_text)

        # TODO: Push to embeddings / DB / pipeline

        processed_files.add(file_id)

    save_processed_files(processed_files)
