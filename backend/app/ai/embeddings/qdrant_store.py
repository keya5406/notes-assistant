import os
import uuid
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


class QdrantStore:
    def __init__(self, collection_name: str, vector_size: int):
        """
        Initialize a connection to Qdrant.
        If the collection doesn't exist, create it with the right vector size.
        """
        self.collection_name = collection_name
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

        # Check if collection exists, if not, create it
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            print(f"[INFO] Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,  # embedding vector size (e.g., 384 for MiniLM)
                    distance=models.Distance.COSINE,  # similarity metric
                ),
            )

    def upsert(self, vectors: list[list[float]], payloads: list[dict]):
        """
        Insert or update (upsert) vectors into Qdrant.
        - vectors: list of embedding vectors
        - payloads: metadata for each vector (e.g., {"text": "...", "file": "doc1.pdf"})

        IDs must be unique. We use uuid4() so every point has a globally unique ID.
        This prevents overwriting old data when uploading new files.
        """
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),  #unique ID for every vector
                    vector=vectors[i],
                    payload=payloads[i],
                )
                for i in range(len(vectors))
            ],
        )

    def query(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """
        Search for the most similar vectors in Qdrant.
        - query_vector: embedding of the query text
        - top_k: how many results to return

        Returns: a list of dicts containing matched text, score, and full payload.
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            {"text": r.payload.get("text"), "score": r.score, "payload": r.payload}
            for r in results
        ]
