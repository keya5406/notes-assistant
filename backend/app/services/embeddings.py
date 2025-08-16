from sentence_transformers import SentenceTransformer

# Load model globally so it's not reloaded on each request
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_question(question: str) -> list[float]:
    # Convert a question into dense vector embedding.
    return _model.encode([question])[0].tolist()
