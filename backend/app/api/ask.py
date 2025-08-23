from fastapi import APIRouter, HTTPException
import app.model.ask_models as ask
import app.services.embeddings as emb
import app.services.retrieval as ret

router = APIRouter()

@router.post("/ask", response_model=ask.AskResponse)
async def ask_question(payload: ask.AskRequest):
    # Validate question
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Embed question
    query_vector = emb.embed_question(question)

    # Retrieve from Qdrant
    results = ret.retrieve_top_k(query_vector, k=5)

    if not results:
        return ask.AskResponse(context="", chunks=[])

    # Sort chunks if metadata has 'order'
    chunks = []
    for res in results:
        payload = res.payload or {}
        chunks.append({
            "text": payload.get("text", ""),
            "source": payload.get("source", "N/A"),
            "order": payload.get("order", None),
            "score": res.score
        })

    chunks.sort(key=lambda x: x["order"] if x["order"] is not None else 9999)

    # Join into context string
    context = "\n".join(chunk["text"] for chunk in chunks if chunk["text"])

    # Return placeholder response
    return ask.AskResponse(
        context=context,
        chunks=chunks
    )