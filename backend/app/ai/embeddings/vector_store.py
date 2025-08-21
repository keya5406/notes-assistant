import chromadb

class VectorStore:
    def __init__(self, collection_name="default"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_embedding(self, embedding, metadata):
        self.collection.add(
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[str(metadata.get("chunk_id", len(self.collection.get()['ids'])))]
        )

    def query(self, query_text, top_k=3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return [
            {"metadata": md, "score": score}
            for md, score in zip(results["metadatas"][0], results["distances"][0])
        ]
