import re

def preprocess_pdf_text(text: str) -> str:
    """Light cleanup of extracted PDF text without deleting all content."""
    if not text:
        return ""

    original_len = len(text)

    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove repeated empty lines (but keep one)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove page numbers alone on a line
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Remove common headers/footers — only if repeated >=3 times
    lines = text.split("\n")
    seen_headers = {}
    for line in lines:
        norm = line.strip()
        if norm:
            seen_headers[norm] = seen_headers.get(norm, 0) + 1

    cleaned_lines = []
    for line in lines:
        norm = line.strip()
        # Remove line if repeated at least 3 times and line length < 80 (header/footer)
        if seen_headers.get(norm, 0) >= 3 and len(norm) < 80:
            continue
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Trim whitespace
    text = text.strip()

    print(f"[DEBUG] Cleaner reduced length from {original_len} to {len(text)}")

    return text
