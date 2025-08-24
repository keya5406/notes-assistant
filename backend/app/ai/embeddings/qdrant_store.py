import os
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

# Load env vars
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


class QdrantStore:
    def __init__(self, collection_name: str, vector_size: int):
        self.collection_name = collection_name
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

        # Create collection if not exists
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            print(f"[INFO] Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert(self, vectors: list[list[float]], payloads: list[dict]):
        """Upsert embeddings with metadata (payloads) into Qdrant."""
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=i,
                    vector=vectors[i],
                    payload=payloads[i],
                )
                for i in range(len(vectors))
            ],
        )

    def query(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """Query most similar texts from Qdrant."""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            {"text": r.payload.get("text"), "score": r.score, "payload": r.payload}
            for r in results
        ]
