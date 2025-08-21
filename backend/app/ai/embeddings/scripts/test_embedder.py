from backend.app.ai.embeddings.embedder import Embedder

def main():
    embedder = Embedder()
    texts = [
        "Machine learning enables computers to learn from data.",
        "Natural Language Processing is a subfield of AI.",
        "FastAPI is great for building APIs quickly."
    ]

    embeddings = embedder.embed_texts(texts)
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Each embedding has {len(embeddings[0])} dimensions")
    print("Sample vector:", embeddings[0][:10])  # print first 10 dims

if __name__ == "__main__":
    main()
