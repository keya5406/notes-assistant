import fitz # pyright: ignore[reportMissingImports]

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF.
    Returns the full text as a single string.
    """
    text_content = []
    with fitz.open(file_path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            text = page.get_text()
            if text:
                text_content.append(text)
    return "\n".join(text_content)

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extracts text form a PDF file provided as raw bytes.
    Useful when downloading directly from Google Drive.
    """
    text_content = []
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page_num, page in enumerate(pdf, start=1):
            text = page.get_text()
            if text:
                text_content.append(text)
    return "\n".join(text_content)