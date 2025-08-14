from typing import List
import re
import nltk
from . import config
from .cleaner import preprocess_pdf_text
from .utils import merge_heading_chunks, cosine_text_similarity, SKLEARN_AVAILABLE

# Download NLTK punkt tokenizer if not already
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from nltk.tokenize import sent_tokenize

try:
    from langchain.text_splitter import TokenTextSplitter
    LANGCHAIN_TOKEN_SPLITTER = True
except Exception:
    LANGCHAIN_TOKEN_SPLITTER = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_CHAR_SPLITTER = True
except Exception:
    LANGCHAIN_CHAR_SPLITTER = False


def dedupe_exact_normalized(chunks: List[str]) -> List[str]:
    seen = set()
    out = []
    for c in chunks:
        norm = re.sub(r'\s+', ' ', c).strip().lower()
        if norm not in seen:
            seen.add(norm)
            out.append(c)
    return out


def semantic_dedupe(chunks: List[str], threshold: float = config.SEMANTIC_SIMILARITY_THRESHOLD) -> List[str]:
    if not SKLEARN_AVAILABLE:
        return chunks
    unique_chunks = []
    for c in chunks:
        if all(cosine_text_similarity(c, u) < threshold for u in unique_chunks):
            unique_chunks.append(c)
    return unique_chunks


def split_into_sections_with_sentence_overlap(
    text: str,
    min_section_tokens: int = 150,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[str]:
    # Step 1: Split based on headings (uppercase lines)
    sections = re.split(r'\n(?=[A-Z][^\n]{0,80}\n)', text)
    merged_sections = []
    buffer = ""

    for sec in sections:
        token_count = len(sec.split())
        if token_count < min_section_tokens:
            buffer += sec + "\n"
        else:
            if buffer.strip():
                merged_sections.append(buffer.strip())
                buffer = ""
            merged_sections.append(sec.strip())

    if buffer.strip():
        merged_sections.append(buffer.strip())

    if len(merged_sections) == 0 and text.strip():
        merged_sections = [text.strip()]

    # Step 2: Sentence-aware chunking with overlap
    final_chunks = []

    for section in merged_sections:
        sentences = sent_tokenize(section)
        if not sentences:
            continue

        start = 0
        while start < len(sentences):
            chunk_sentences = []
            token_count_in_chunk = 0
            idx = start
            # Add sentences until we reach chunk_size tokens
            while idx < len(sentences) and token_count_in_chunk + len(sentences[idx].split()) <= chunk_size:
                chunk_sentences.append(sentences[idx])
                token_count_in_chunk += len(sentences[idx].split())
                idx += 1

            if not chunk_sentences:
                # fallback: take at least one sentence
                chunk_sentences.append(sentences[start])
                idx = start + 1

            final_chunks.append(" ".join(chunk_sentences))

            if idx >= len(sentences):
                break

            # Move start pointer with overlap in sentences
            # Convert chunk_overlap in tokens to approximate sentences
            overlap_sent_count = 0
            tokens_seen = 0
            for s in reversed(chunk_sentences):
                tokens_seen += len(s.split())
                overlap_sent_count += 1
                if tokens_seen >= chunk_overlap:
                    break
            start = idx - overlap_sent_count

    return final_chunks


def chunk_text(raw_text: str,
               chunk_size: int = 500,
               chunk_overlap: int = 50,
               use_semantic_dedupe: bool = False) -> List[str]:

    chunk_size = chunk_size or config.CHUNK_SIZE_TOKENS
    chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP_TOKENS

    if not raw_text or not raw_text.strip():
        return []

    print("\n\n=== DEBUG: TEXT RECEIVED FOR CHUNKING ===")
    print(raw_text[:2000])
    print("=== END OF TEXT RECEIVED ===\n\n")

    # 1) Clean text
    text = preprocess_pdf_text(raw_text)

    # 2) Smart chunking: sentence-aware + heading sections + overlap
    chunks = split_into_sections_with_sentence_overlap(
        text,
        min_section_tokens=150,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # 3) Remove empty chunks & exact duplicates
    chunks = dedupe_exact_normalized(chunks)

    # 4) Semantic deduplication if enabled
    if use_semantic_dedupe:
        chunks = semantic_dedupe(chunks)

    # 5) Merge heading chunks (optional)
    chunks = merge_heading_chunks(chunks)

    print("\n\n=== DEBUG: CHUNKS GENERATED ===")
    for i, chunk in enumerate(chunks):
        print(f"\n--- CHUNK {i + 1} ---\n{chunk}\n")
    print("=== END OF CHUNKS ===\n\n")

    return chunks
