"""
This script checks if a given PDF file contains an OCR (Optical Character Recognition) layer.
It uses the `fitz` module from the PyMuPDF library to read the PDF and analyze its text content.

Dependencies:
- fitz (PyMuPDF): Install using `pip install PyMuPDF`

Usage:
Save the script in a Python file (e.g., `check_ocr.py`), and run it in your terminal:
python check_ocr.py

Replace `"sample.pdf"` with the path to the PDF file you want to check.
"""

import fitz

def has_ocr(pdf_path):
    """
    Checks if the PDF at the given path contains an OCR layer.

    Parameters:
    pdf_path (str): The path to the PDF file to be checked.

    Returns:
    bool: True if any page in the PDF has text content (indicating an OCR layer), 
          False if no pages contain text or if an error occurs.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            if text.strip():
                return True
        return False
    except Exception as e:
        print("An error occurred:", e)
        return False

# Path to the PDF file to be checked
pdf_path = "sample.pdf"

# Check if the PDF has an OCR layer and print the result
if has_ocr(pdf_path):
    print("PDF has OCR layer.")
else:
    print("PDF does not have OCR layer.")
