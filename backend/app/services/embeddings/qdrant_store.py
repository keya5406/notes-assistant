import os
import uuid
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

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

        # Ensure payload index exists
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="subject_code",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
        except Exception as e:
            print(f"[INFO] Payload index for 'subject_code' already exists or failed: {e}")

    def upsert(self, vectors: list[list[float]], payloads: list[dict]):
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[i],
                payload=payloads[i],
            )
            for i in range(len(vectors))
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"[INFO] {len(vectors)} vectors inserted")

    def query(self, query_vector: list[float], subject_code: str = None, top_k: int = 5) -> list[dict]:
        query_filter = None
        if subject_code:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="subject_code",
                        match=models.MatchValue(value=subject_code),
                    )
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
        )

        return [
            {"text": r.payload.get("text"), "score": r.score, "payload": r.payload}
            for r in results
        ]
