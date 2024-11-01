from .local_files import get_local_documents
from .ocr import has_ocr, extract_text_doctr
from .llm import query_prompt

__all__ = ['get_local_documents' , 'has_ocr', 'extract_text_doctr', 'query_prompt']
