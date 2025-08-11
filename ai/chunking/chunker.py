from typing import List
import re
from . import config
from .cleaner import preprocess_pdf_text
from .utils import (
    merge_heading_chunks,
    count_tokens,
    cosine_text_similarity, SKLEARN_AVAILABLE
)

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


def simple_token_split(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    tokens = text.split()
    if not tokens:
        return []
    chunks = []
    i = 0
    n = len(tokens)
    while i < n:
        j = min(n, i + chunk_size)
        chunks.append(" ".join(tokens[i:j]).strip())
        if j == n:
            break
        i = j - chunk_overlap
    return chunks


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


def safe_chunk_text(text: str) -> List[str]:
    if LANGCHAIN_TOKEN_SPLITTER:
        splitter = TokenTextSplitter(
            chunk_size=config.CHUNK_SIZE_TOKENS,
            chunk_overlap=config.CHUNK_OVERLAP_TOKENS,
            encoding_name="cl100k_base"
        )
        return splitter.split_text(text)
    elif LANGCHAIN_CHAR_SPLITTER:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=[
                "\n\n",
                ". ",
                " ",
                ""
            ]
        )
        return splitter.split_text(text)
    else:
        return simple_token_split(text, config.CHUNK_SIZE_TOKENS, config.CHUNK_OVERLAP_TOKENS)


def split_into_sections(text: str) -> List[str]:
    # Match headings like "Chapter", "Section", or numbered headings like "1.", "2)", etc.
    pattern = re.compile(
        r'(^\s*(?:Chapter|Section|\d+[\.\)\-])[\s\S]*?)(?=^\s*(?:Chapter|Section|\d+[\.\)\-])|\Z)',
        re.MULTILINE | re.IGNORECASE
    )
    sections = pattern.findall(text)
    if not sections:
        return [text]
    return sections


def chunk_text(raw_text: str,
               chunk_size: int = None,
               chunk_overlap: int = None,
               use_semantic_dedupe: bool = False) -> List[str]:
    chunk_size = chunk_size or config.CHUNK_SIZE_TOKENS
    chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP_TOKENS

    if not raw_text or not raw_text.strip():
        return []

    # 1) Clean the raw text
    text = preprocess_pdf_text(raw_text)

    # 2) Split into sections by headings
    sections = split_into_sections(text)

    # 3) For each section, chunk text safely (token-aware)
    all_chunks = []
    for sec in sections:
        sub_chunks = safe_chunk_text(sec)
        all_chunks.extend([c.strip() for c in sub_chunks if c.strip()])

    # 4) Remove empty chunks and exact normalized duplicates
    chunks = [c.strip() for c in all_chunks if c.strip()]
    chunks = dedupe_exact_normalized(chunks)

    # 5) Optionally do semantic deduplication
    if use_semantic_dedupe:
        chunks = semantic_dedupe(chunks)

    # 6) Optionally merge heading chunks for better context (optional)
    chunks = merge_heading_chunks(chunks)

    return chunks
