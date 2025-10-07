from fastapi import APIRouter, HTTPException
from ..services.drive_ingestor import sync_drive_folder

router = APIRouter()


@router.post("/sync-drive")
async def sync_drive():
    """
    Trigger a Google Drive sync manually.
    Downloads new PDFs, extracts text, chunks, embeds, and stores in Qdrant.
    """
    try:
        sync_drive_folder()
        return {
            "status": "success",
            "message": "Drive sync completed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive sync failed: {str(e)}")
