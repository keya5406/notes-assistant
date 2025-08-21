import os
from backend.app.ai.chunking.chunker import chunk_text
from backend.app.ai.embeddings.embedder import Embedder
from backend.app.ai.embeddings.vector_store import VectorStore

def main():
    # 1. Load text file
    file_path = "sample_text_3.txt"  # change to your file
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # 2. Chunk text
    chunks = chunk_text(raw_text)
    print(f"✅ Generated {len(chunks)} chunks")

    # 3. Init embedder + vector store
    embedder = Embedder()
    vector_store = VectorStore(collection_name="test_docs")

    # 4. Embed + store
    for i, chunk in enumerate(chunks):
        embedding = embedder.embed(chunk)
        vector_store.add_embedding(
            embedding=embedding,
            metadata={"chunk_id": i, "text": chunk}
        )

    # 5. Query
    query = "applications of trees?"
    results = vector_store.query(query, top_k=3)

    print(f"\n🔍 Query: {query}")
    for r in results:
        print(f" -> {r['metadata']['text']} | Score: {r['score']:.4f}")

if __name__ == "__main__":
    main()
