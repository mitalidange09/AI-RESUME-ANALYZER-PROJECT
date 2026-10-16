import os
import re

from PyPDF2 import PdfReader
from docx import Document


def extract_pdf_text(file_path):
    text_blocks = []
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            content = page.extract_text() or ''
            if content:
                text_blocks.append(content)
        return '\n'.join(text_blocks)
    except Exception:
        return ''


def extract_docx_text(file_path):
    try:
        document = Document(file_path)
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        return '\n'.join(paragraphs)
    except Exception:
        return ''


def extract_resume_text(file_path):
    if not file_path or not os.path.exists(file_path):
        return ''

    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        text = extract_pdf_text(file_path)
    elif ext == '.docx':
        text = extract_docx_text(file_path)
    else:
        text = ''

    if text:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
    return text
