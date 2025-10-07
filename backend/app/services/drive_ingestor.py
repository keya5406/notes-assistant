import os
import json
import re
from dotenv import load_dotenv
from pathlib import Path

import backend.app.utils.google_drive as google_drive
import backend.app.services.extractor as ext
from backend.app.ai.chunking.chunker import chunk_text
from backend.app.ai.embeddings.dependencies import embedder, qdrant_store

BASE_DIR = Path(__file__).parent.parent
PROCESSED_FILE_PATH = BASE_DIR / "db" / "processed_files.json"

load_dotenv()
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")


def load_processed_files():
    if PROCESSED_FILE_PATH.exists():
        try:
            with open(PROCESSED_FILE_PATH, "r") as f:
                data = f.read().strip()
                if not data:
                    return set()
                return set(json.loads(data))
        except json.JSONDecodeError:
            return set()
    return set()


def save_processed_files(processed_files):
    with open(PROCESSED_FILE_PATH, "w") as f:
        json.dump(list(processed_files), f, indent=2)


# ... same imports and helper functions ...

def sync_drive_folder(batch_size: int = 5):
    """
    Sync PDFs from nested structure: Root → Semester → Subject → Files.
    Subject code = file name (without .pdf).
    Processes `batch_size` PDFs at a time.
    """
    if not DRIVE_FOLDER_ID:
        raise ValueError("DRIVE_FOLDER_ID not set in environment variables")

    processed_files = load_processed_files()
    total_chunks = 0
    batch_count = 0

    def process_folder(folder_id: str):
        nonlocal total_chunks, batch_count
        items = google_drive.list_files_in_folder(folder_id)

        for item in items:
            if batch_count >= batch_size:
                return

            if item["mimeType"] == "application/vnd.google-apps.folder":
                process_folder(item["id"])

            elif item["mimeType"] == "application/pdf":
                file_id = item["id"]
                file_name = item["name"]
                subject_code = re.sub(r"\.pdf$", "", file_name, flags=re.IGNORECASE)

                if file_id in processed_files:
                    continue

                print(f"⬇️ Downloading {file_name}")
                file_bytes = google_drive.download_file(file_id)

                # Extract text
                extracted_text = ext.extract_text_from_pdf_bytes(file_bytes)
                extracted_text = extracted_text.encode("utf-8", errors="ignore").decode("utf-8")
                extracted_text = extracted_text.replace("\r\n", "\n").strip()
                extracted_text = re.sub(r"\n{2,}", "\n\n", extracted_text)

                # Chunk text
                chunks = chunk_text(extracted_text, chunk_size=500, chunk_overlap=50, use_semantic_dedupe=False)
                if not chunks:
                    processed_files.add(file_id)
                    continue

                # Embed chunks
                embeddings = embedder.embed_texts(chunks)


                # Create payloads
                payloads = [
                    {"chunk_index": i, "text": chunks[i], "subject_code": subject_code}
                    for i in range(len(chunks))
                ]

                # Upsert into Qdrant
                qdrant_store.upsert(embeddings, payloads)
                total_chunks += len(chunks)
                batch_count += 1
                processed_files.add(file_id)
                print(f"Stored {len(chunks)} chunks for {file_name} (subject: {subject_code})")

                if batch_count >= batch_size:
                    return

    print(f"Root folder ID: {DRIVE_FOLDER_ID}")
    process_folder(DRIVE_FOLDER_ID)

    save_processed_files(processed_files)
    print(f"\nDrive sync completed. Total chunks stored: {total_chunks} (processed {batch_count} files this run)")
