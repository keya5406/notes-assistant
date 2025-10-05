from typing import List
import backend.app.db.qdrant_conn as qd

def retrieve_top_k(query_embedding: List[float], k: int = 5):
    # Query Qdrant for top-k most similar chunks.
    results = qd.client.search(
        collection_name=qd.QDRANT_COLLECTION,
        query_vector=query_embedding,
        limit=k,
        with_payload=True,
        with_vectors=False,
    )
    return results
