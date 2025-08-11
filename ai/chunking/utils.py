import re
from typing import List

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except Exception:
    TIKTOKEN_AVAILABLE = False

def is_heading(line: str) -> bool:
    """
    Heuristic for headings:
      - numbered like "1.", "2)", "1 -", "1 –"
      - markdown style: '#'
      - or ALL CAPS short lines
      - lines starting with Chapter/Section keywords
    """
    if not line:
        return False
    s = line.strip()
    if s.startswith('#'):
        return True
    if re.match(r'^\d+(\.\d+)*\s*[\.\-\)\–]\s*', s):
        return True
    if s.isupper() and 2 < len(s) < 120:
        return True
    if re.match(r'^(Chapter|CHAPTER|Section|SECTION)\b', s, flags=re.IGNORECASE):
        return True
    return False

def merge_heading_chunks(chunks: List[str]) -> List[str]:
    merged_chunks = []
    skip_next = False
    for i in range(len(chunks)):
        if skip_next:
            skip_next = False
            continue
        chunk = chunks[i].strip()
        if is_heading(chunk) and i + 1 < len(chunks):
            # Merge heading with next chunk to keep context
            merged = chunk + " " + chunks[i + 1].strip()
            merged_chunks.append(merged)
            skip_next = True
        else:
            merged_chunks.append(chunk)
    return merged_chunks

def clean_leading_chars(chunk: str) -> str:
    return re.sub(r'^[\.\-•\s]+', '', chunk).strip()

def count_tokens(text: str, model: str = None) -> int:
    """
    Token counting function:
    - If tiktoken available, use a default encoding (cl100k_base) for rough token count.
    - Otherwise fallback to word count.
    """
    if not text:
        return 0
    if TIKTOKEN_AVAILABLE:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            enc = tiktoken.encoding_for_model(model) if model else tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    # fallback: words count
    return len(text.split())

# Optional: semantic similarity if sklearn available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

def cosine_text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if SKLEARN_AVAILABLE:
        vec = TfidfVectorizer().fit_transform([a, b])
        return float(cosine_similarity(vec[0], vec[1])[0][0])
    # fallback: simple Jaccard-like similarity
    a_set = set(a.lower().split())
    b_set = set(b.lower().split())
    if not a_set or not b_set:
        return 0.0
    inter = a_set & b_set
    uni = a_set | b_set
    return len(inter) / len(uni)
