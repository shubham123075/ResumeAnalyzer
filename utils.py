from pathlib import Path

from docx import Document
import PyPDF2

def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    
    return text


def extract_text_from_docx(file):
    document = Document(file)
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)


def extract_text(file):
    filename = getattr(file, "filename", str(file)).lower()
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file)

    if suffix == ".docx":
        return extract_text_from_docx(file)

    if suffix == ".txt":
        if hasattr(file, "read"):
            return file.read().decode("utf-8", errors="ignore")
        return Path(file).read_text(encoding="utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT resume.")
