"""
Module for OCR (Optical Character Recognition) utilities.

This module provides functions for checking if a PDF has an OCR layer,
extracting text using OCR, and extracting text from PDFs with existing text layers.

Dependencies:
- fitz (PyMuPDF): For PDF processing
- torch: For GPU acceleration in OCR
- doctr: For advanced OCR capabilities
"""

import fitz
import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor


def has_ocr(pdf_path):
    """
    Check if a PDF file has an OCR layer.

    This function attempts to extract text from each page of the PDF.
    If any page contains extractable text, it assumes the PDF has an OCR layer.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        bool: True if the PDF has extractable text, False otherwise.

    Raises:
        Exception: If there's an error opening or processing the PDF.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        for page in pdf_document:
            if page.get_text().strip():
                return True
        return False
    except Exception as e:
        print(f"An error occurred while checking for OCR: {e}")
        return False


def extract_text_doctr(pdf_path, enable_ocr_gpu=True):
    """
    Extract text from a PDF using the doctr OCR library.

    This function uses advanced OCR capabilities to extract text from PDFs,
    including those without an existing text layer.

    Args:
        pdf_path (str): Path to the PDF file.
        enable_ocr_gpu (bool): Whether to use GPU acceleration for OCR.

    Returns:
        str: Extracted text from the PDF, or None if an error occurs.

    Raises:
        Exception: If there's an error during the OCR process.
    """
    try:
        device = torch.device("cuda:0" if enable_ocr_gpu and
                                          torch.cuda.is_available() else "cpu")
        model = ocr_predictor(pretrained=True).to(device)

        doc = DocumentFile.from_pdf(pdf_path)
        result = model(doc)

        text = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    text += '\n' + ' '.join(word.value for word in line.words)

        return text.strip()
    except Exception as e:
        print(f"An error occurred during OCR: {e}")
        return None


def extract_text_from_pdf_file(pdf_path):
    """
    Extract text from a PDF file with an existing text layer.

    This function uses PyMuPDF (fitz) to extract text from PDFs that already
    have a text layer, without performing OCR.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF, or None if an error occurs.

    Raises:
        Exception: If there's an error opening or processing the PDF.
    """
    try:
        with fitz.open(pdf_path) as pdf_document:
            return " ".join(page.get_text() for page in pdf_document)
    except Exception as e:
        print(f"An error occurred while extracting text: {e}")
        return None
