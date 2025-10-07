from backend.app.services.embeddings.embedder import Embedder
from backend.app.services.embeddings.qdrant_store import QdrantStore

# Initialize shared instances
embedder = Embedder()
qdrant_store = QdrantStore(collection_name="notes", vector_size=384)
