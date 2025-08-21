from backend.app.ai.embeddings.vector_store import VectorStore

def main():
    store = VectorStore()

    # Example texts
    docs = [
        "Deep learning models require large datasets.",
        "Transformers revolutionized NLP.",
        "ChromaDB is a vector database for embeddings."
    ]

    # Store documents
    store.add_texts(docs, ids=["1", "2", "3"])

    # Run a query
    query = "What is used for natural language processing?"
    results = store.query(query, n_results=2)

    print("\nQuery:", query)
    for doc, score in zip(results['documents'][0], results['distances'][0]):
        print(f" -> {doc} | Score: {score:.4f}")

if __name__ == "__main__":
    main()
