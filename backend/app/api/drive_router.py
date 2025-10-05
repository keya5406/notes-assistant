from fastapi import  APIRouter
from backend.app.services.drive_ingestor import sync_drive_folder

router = APIRouter()

@router.post("/sync-drive")
async def sync_drive():
    """
    Trigger a Google Drive sync manually.
    """
    try:
        sync_drive_folder()
        return {
            "status": "success",
            "message": "Drive sync completed.",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }