from fastapi import APIRouter, HTTPException
from app.model.ask_models import AskRequest, AskResponse

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(payload: AskRequest):
    # Step 1: Validate question
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Step 2: Return placeholder response
    # Later: embed question -> retrieve from Qdrant -> build context
    return AskResponse(
        context="This is a placeholder context until retrieval logic is implemented.",
        chunks=[]
    )