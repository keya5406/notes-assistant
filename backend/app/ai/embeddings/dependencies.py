from backend.app.ai.embeddings.embedder import Embedder
from backend.app.ai.embeddings.qdrant_store import QdrantStore

# Initialize shared instances
embedder = Embedder()
qdrant_store = QdrantStore(collection_name="notes", vector_size=384)
