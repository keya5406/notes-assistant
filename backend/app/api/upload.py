import os
import shutil
import re
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.services.extractor import extract_text_from_pdf
from backend.app.ai.chunking.chunker import chunk_text
from backend.app.ai.embeddings.dependencies import embedder, qdrant_store

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
        # Step 1: Extract raw text
        extracted_text = extract_text_from_pdf(temp_file_path)

        # Step 2: Clean text
        extracted_text = extracted_text.encode("utf-8", errors="ignore").decode("utf-8")
        extracted_text = extracted_text.replace("\r\n", "\n").strip()
        extracted_text = re.sub(r"\n{2,}", "\n\n", extracted_text)

        # Step 3: Chunk text
        chunks = chunk_text(
            extracted_text,
            chunk_size=500,
            chunk_overlap=50,
            use_semantic_dedupe=False
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="No valid chunks generated from document.")

        # Step 4: Embed chunks
        embeddings = embedder.embed_texts(chunks)

        # Step 5: Build payloads (store text + source filename)
        payloads = [{"text": chunks[i], "source": file.filename} for i in range(len(chunks))]

        # Step 6: Store in Qdrant
        qdrant_store.upsert(embeddings, payloads)

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
