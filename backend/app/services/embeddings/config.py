from pathlib import Path
import torch

# Embedding Model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Vector DB Config
CHROMA_DB_PATH = Path("data/chroma_db")
COLLECTION_NAME = "notes_embeddings"

# Batch Settings
BATCH_SIZE = 32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"