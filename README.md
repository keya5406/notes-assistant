# 🧩 Google Drive PDF Syncing — Feature Overview

### **Branch:** `feature/nat-7-drive-sync`  
### **Purpose:**  
Automates fetching, processing, and extracting text from PDF files stored in a connected Google Drive folder.

---

## 🚀 Key Features Added
- **Google Drive API integration**  
  Establishes a secure connection using `credentials.json` (OAuth2) and auto-generates `token.pickle` for authentication persistence.  

- **Automated PDF fetching**  
  The script automatically scans a target Drive folder for newly added PDFs and downloads them for processing.

- **Raw byte-based text extraction**  
  Improved the PDF extraction logic to handle direct byte streams — ensuring higher reliability and better compatibility.

- **Processed files tracking**  
  Introduced `processed_files.json` to maintain a record of already-processed file IDs, preventing duplicate extractions.

- **Configurable credentials and paths**  
  Added flexible path definitions for credentials and processed file logs using Python’s `pathlib` and `os.path`.

---

## 🔧 Implementation Details
- Core logic lives in:  
  ```
  backend/app/utils/google_drive.py  
  backend/app/services/extractor.py  
  backend/app/routes/drive_ingestor.py
  ```
- Persistent record file:  
  ```
  backend/app/db/processed_files.json
  ```
- Secrets stored in:  
  ```
  backend/app/secrets/credentials.json
  ```

---

## 🧠 Future Enhancements
- Detect **replaced or updated Drive files** (via `version` or `modifiedTime` checks).  
- Add **periodic sync scheduling** (e.g., via FastAPI background task or CRON).  
- Integrate directly into the **notes preprocessing pipeline** for real-time content updates.

---

## 💡 Why This Matters
This feature automates one of the most time-consuming parts of the pipeline — manual data ingestion.  
Now, any new or updated PDF added to Google Drive can be auto-fetched, processed, and made ready for downstream tasks like summarization, embedding, or RAG querying.
