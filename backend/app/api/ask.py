from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.ai.embeddings.dependencies import embedder, qdrant_store

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    top_k: int = 3

@router.post("/ask")
async def ask_question(request: AskRequest):
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Step 1: Embed the question
        query_vector = embedder.embed_texts([question])[0]

        # Step 2: Query Qdrant
        results = qdrant_store.query(query_vector, top_k=request.top_k)
        if not results:
            return {
                "status": "success",
                "question": question,
                "chunks": []
            }

        # Step 3: Extract chunks
        chunks = []
        for r in results:
            if isinstance(r, dict):
                text = r.get("text", "")
                score = r.get("score", None)
            else:  # Qdrant ScoredPoint
                text = getattr(r, "payload", {}).get("text", "")
                score = getattr(r, "score", None)
            chunks.append({"text": text, "score": score})

        # Step 4: Return only question + chunks
        return {
            "status": "success",
            "question": question,
            "chunks": chunks
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
