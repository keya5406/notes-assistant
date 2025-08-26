from fastapi import  APIRouter
from app.services.drive_ingestor import sync_drive_folder

router = APIRouter(tags=["Drive"])

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