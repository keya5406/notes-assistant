from typing import List
import re
import nltk
from . import config
from .cleaner import preprocess_pdf_text
from .utils import merge_heading_chunks, cosine_text_similarity, SKLEARN_AVAILABLE

# Ensure NLTK sentence tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from nltk.tokenize import sent_tokenize

# Try importing LangChain splitter
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except Exception:
    LANGCHAIN_AVAILABLE = False


def dedupe_exact_normalized(chunks: List[str]) -> List[str]:
    """Remove exact duplicates (case and whitespace insensitive)."""
    seen = set()
    unique = []
    for chunk in chunks:
        norm = re.sub(r'\s+', ' ', chunk).strip().lower()
        if norm not in seen:
            seen.add(norm)
            unique.append(chunk)
    return unique


def semantic_dedupe(
    chunks: List[str],
    threshold: float = config.SEMANTIC_SIMILARITY_THRESHOLD
) -> List[str]:
    """Optionally remove semantically similar chunks using cosine similarity."""
    if not SKLEARN_AVAILABLE:
        return chunks

    unique_chunks = []
    for chunk in chunks:
        if all(cosine_text_similarity(chunk, u) < threshold for u in unique_chunks):
            unique_chunks.append(chunk)
    return unique_chunks


def sentence_chunker(
    text: str,
    chunk_size: int,
    chunk_overlap: int
) -> List[str]:
    """
    Sentence-aware chunker with token overlap (used if LangChain unavailable).
    """
    sections = re.split(r'\n(?=[A-Z][^\n]{0,80}\n)', text)
    merged_sections, buffer = [], ""

    # Merge short sections with previous ones
    for sec in sections:
        token_count = len(sec.split())
        if token_count < 150:
            buffer += sec + "\n"
        else:
            if buffer.strip():
                merged_sections.append(buffer.strip())
                buffer = ""
            merged_sections.append(sec.strip())

    if buffer.strip():
        merged_sections.append(buffer.strip())

    if not merged_sections and text.strip():
        merged_sections = [text.strip()]

    final_chunks = []
    for section in merged_sections:
        sentences = sent_tokenize(section)
        if not sentences:
            continue

        start = 0
        while start < len(sentences):
            chunk_sentences, token_count = [], 0

            # Build each chunk by sentence length
            while (
                start + len(chunk_sentences) < len(sentences)
                and token_count + len(sentences[start + len(chunk_sentences)].split()) <= chunk_size
            ):
                s = sentences[start + len(chunk_sentences)]
                chunk_sentences.append(s)
                token_count += len(s.split())

            if not chunk_sentences:
                chunk_sentences = [sentences[start]]

            chunk = " ".join(chunk_sentences)
            final_chunks.append(chunk)

            # Calculate overlap in sentences
            overlap_tokens, overlap_sentences = 0, 0
            for s in reversed(chunk_sentences):
                overlap_tokens += len(s.split())
                overlap_sentences += 1
                if overlap_tokens >= chunk_overlap:
                    break

            start += len(chunk_sentences) - overlap_sentences

    return final_chunks


def chunk_text(
    raw_text: str,
    chunk_size: int = config.CHUNK_SIZE_TOKENS,
    chunk_overlap: int = config.CHUNK_OVERLAP_TOKENS,
    use_semantic_dedupe: bool = False
) -> List[str]:
    """Main entry for chunking text into semantically meaningful pieces."""

    if not raw_text or not raw_text.strip():
        return []

    # 1️⃣ Clean raw text
    cleaned_text = preprocess_pdf_text(raw_text)

    # 2️⃣ Use LangChain splitter if available
    if LANGCHAIN_AVAILABLE:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: len(x.split()),  # approximate token count
            separators=["\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_text(cleaned_text)
    else:
        # fallback to custom sentence-aware splitter
        chunks = sentence_chunker(cleaned_text, chunk_size, chunk_overlap)

    # 3️⃣ Deduplicate exact text
    chunks = dedupe_exact_normalized(chunks)

    # 4️⃣ Optional semantic deduplication
    if use_semantic_dedupe:
        chunks = semantic_dedupe(chunks)

    # 5️⃣ Merge heading-based sections for cohesion
    chunks = merge_heading_chunks(chunks)

    return chunks
