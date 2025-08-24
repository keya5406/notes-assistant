from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.ai.embeddings.dependencies import embedder, qdrant_store

router = APIRouter()

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: AskRequest):
    try:
        # Get and validate question
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Embed the question
        query_vector = embedder.embed_texts([question])[0]

        # Query Qdrant
        results = qdrant_store.query(query_vector, top_k=3)

        if not results:
            return {"status": "success", "context": "", "chunks": []}

        # Prepare chunks
        chunks = []
        for r in results:
            chunks.append({
                "text": r["text"],
                "score": r["score"]
            })

        # Build context
        context = "\n".join(chunk["text"] for chunk in chunks if chunk["text"])

        return {
            "status": "success",
            "context": context,
            "chunks": chunks
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in ask API: {str(e)}")
