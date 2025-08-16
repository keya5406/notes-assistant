import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
import app.services.extractor as ext

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # 1. Validate file presence
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    # 2. Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 3. Save to temporary location
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 4. Extract text
        extracted_text = ext.extract_text_from_pdf(temp_file_path)

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF.")

        return {
            "status": "success",
            "filename": file.filename,
            "text": extracted_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 5. Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
