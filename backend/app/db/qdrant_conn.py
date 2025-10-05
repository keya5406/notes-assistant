import os
from qdrant_client import QdrantClient
# from dotenv import load_dotenv
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(":memory:")

COLLECTION_NAME = "notes_demo"

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=4, distance=Distance.COSINE),
)

dummy_points = [
    PointStruct(
        id=1,
        vector=[0.1, 0.2, 0.3, 0.4],
        payload={"text": "Artificial Intelligence is the simulation of human intelligence."},
    ),
    PointStruct(
        id=2,
        vector=[0.2, 0.1, 0.4, 0.3],
        payload={"text": "Machine Learning is a subset of AI that uses data-driven algorithms."},
    ),
    PointStruct(
        id=3,
        vector=[0.3, 0.3, 0.2, 0.1],
        payload={"text": "Qdrant is a vector database optimized for semantic search."},
    ),
]

client.upsert(
    collection_name=COLLECTION_NAME,
    points=dummy_points
)