import os
import io
import fitz
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import torch

def has_ocr(self):
    """
    Check if the provided PDF bytes contain any text (indicating OCR).
    
    :param pdf_bytes: The PDF content as a bytes-like object.
    :return: True if the PDF has text; False otherwise.
    """
    try:
        # Load the PDF from bytes
        pdf_bytes = self.config.get_shared_state('current_file')
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            if text.strip():
                return True
        return False
    except Exception as e:
        self.logger.error(f"An error occurred in has_ocr: {e}")
        return False

def extract_text_from_pdf_file(self):
    """
    Extract text from the provided PDF bytes.

    :param pdf_bytes: The PDF content as a bytes-like object.
    :return: True if text extraction is successful; False otherwise.
    """
    text = ''
    try:
        # Load the PDF from bytes
        pdf_bytes = self.config.get_shared_state('current_file')
        with io.BytesIO(pdf_bytes) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text() or ''  # Handle potential None return
        self.ocr_text = text
        return True
    except Exception as e:
        self.logger.error(f"An error occurred in extract_text_from_pdf_file: {e}")
        return False

def extract_text_doctr(self):
    """
    Extract text from the provided PDF bytes using OCR.

    :param pdf_bytes: The PDF content as a bytes-like object.
    :return: True if text extraction is successful; False otherwise.
    """
    text = ''
    try:
        if self.enable_ocr_gpu:
            self.logger.info("OCR using GPU")
            device = torch.device(self.config.get('ocr.device'))
            model = ocr_predictor(pretrained=True).to(device)
        else:
            self.logger.info("OCR using CPU")
            model = ocr_predictor(pretrained=True)
        
        # Load the PDF from bytes
        pdf_bytes = self.config.get_shared_state('current_file')
        pdf_io = io.BytesIO(pdf_bytes)
        doc = DocumentFile.from_pdf(pdf_io)

        self.logger.info("OCR started.")
        result = model(doc)
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    text += '\n'
                    for word in line.words:
                        text += word.value + ' '
        
        self.ocr_text = text
        self.logger.info("OCR completed.")
        return True
    except Exception as e:
        self.logger.error(f"An error occurred in extract_text_doctr: {e}")
        return False