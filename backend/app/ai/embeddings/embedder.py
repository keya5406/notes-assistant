from backend.app.ai.embeddings.config import EMBEDDING_MODEL_NAME, DEVICE


class Embedder:
    def __init__(self, model_name=EMBEDDING_MODEL_NAME, device=DEVICE):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name, device=device)

    def embed_texts(self, texts: list[str]):
        """Embeds a list of texts and returns a list of vectors."""
        return self.model.encode(texts, convert_to_tensor=False).tolist()

    def embed(self, text: str):
        """Embed a single text string."""
        return self.embed_texts([text])[0]
