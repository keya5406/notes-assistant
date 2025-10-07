from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.app.ai.embeddings.dependencies import embedder, qdrant_store
from backend.app.services.llm_service import get_answer_from_context

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    top_k: int = 3
    subject_code: str | None = None  # optional filter by subject_code

@router.post("/ask")
async def ask_question(request: AskRequest):
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Step 1: Embed the question
        query_vector = embedder.embed_texts([question])[0]

        # Step 2: Query Qdrant
        results = qdrant_store.query(
            query_vector,
            top_k=request.top_k,
            subject_code=request.subject_code  # filter by subject_code if provided
        )

        if not results:
            return {
                "status": "success",
                "question": question,
                "chunks": []
            }

        # Step 3: Extract chunks
        chunks = [
            {"text": r.get("text", ""), "score": r.get("score")}
            for r in results
        ]

        # Step 4: Call LLM
        answer = await get_answer_from_context(chunks, question)

        return {
            "status": "success",
            "question": question,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
