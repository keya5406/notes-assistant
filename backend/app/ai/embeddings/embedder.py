from backend.app.ai.embeddings.config import EMBEDDING_MODEL_NAME, DEVICE
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name=EMBEDDING_MODEL_NAME, device=DEVICE):
        self.model = SentenceTransformer(model_name, device=device)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts into vectors."""
        return self.model.encode(texts, convert_to_tensor=False).tolist()

    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a vector."""
        return self.embed_texts([text])[0]
