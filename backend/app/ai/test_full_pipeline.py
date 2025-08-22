from backend.app.ai.chunking.chunker import chunk_text
from backend.app.ai.embeddings.embedder import Embedder
from backend.app.ai.embeddings.qdrant_store import QdrantStore


def main():
    # 1. Load document
    with open("sample_text_3.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    # 2. Chunk text
    chunks = chunk_text(raw_text)
    print(f"✅ Generated {len(chunks)} chunks")

    # 3. Embed chunks
    embedder = Embedder()
    vectors = embedder.embed_texts(chunks)

    # 4. Store in Qdrant Cloud (env handled inside QdrantStore)
    store = QdrantStore(
        collection_name="notes_collection",
        vector_size=len(vectors[0]),
    )
    store.add(vectors, chunks)
    print("✅ Stored chunks in Qdrant Cloud")

    # 5. Query
    query = "What is tree?"
    query_embedding = embedder.embed(query)
    results = store.query(query_embedding, top_k=3)

    print("\n=== QUERY RESULTS ===")
    for text, score in results:
        print(f"[{score:.4f}] {text}")


if __name__ == "__main__":
    main()
