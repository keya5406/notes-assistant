# Chunking size & behavior (tokens preferred, falls back to words)
CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50

# When detecting repeated header/footer lines:
HEADER_FOOTER_MIN_REPEATS = 3       # min occurrences to consider a line repeated
HEADER_FOOTER_MAX_LINE_LENGTH = 200 # ignore very long lines when detecting repeats
HEADER_FOOTER_PAGE_RATIO = 0.05     # also consider lines that appear in >5% pages

# Merge/cleanup thresholds
MIN_CHUNK_CHARS_TO_MERGE = 200
MIN_SECTION_WORDS_TO_KEEP = 50

# Deduplication threshold (optional semantic dedupe if sklearn installed)
SEMANTIC_SIMILARITY_THRESHOLD = 0.85  # if using semantic dedupe (cosine)
