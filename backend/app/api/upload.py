import os
import shutil
import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.extractor import extract_text_from_pdf
from app.ai.chunking.chunker import chunk_text

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(temp_file_path)

        # === DEBUG: raw text check ===
        print("\n\n=== DEBUG: API Extractor Output ===")
        print(f"Total characters: {len(extracted_text)}")
        print("FIRST 500 CHARS:\n", extracted_text[:500])
        print("\n---\nLAST 500 CHARS:\n", extracted_text[-500:])
        print("=== END DEBUG ===\n\n")

        # Normalize text
        extracted_text = extracted_text.encode("utf-8", errors="ignore").decode("utf-8")
        extracted_text = extracted_text.replace("\r\n", "\n").strip()
        extracted_text = re.sub(r'\n{2,}', '\n\n', extracted_text)

        chunks = chunk_text(extracted_text, chunk_size=500, chunk_overlap=50, use_semantic_dedupe=False)

        return {
            "status": "success",
            "filename": file.filename,
            "total_chunks": len(chunks),
            "raw_text_length": len(extracted_text),
            "chunks_preview": chunks[:3]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
