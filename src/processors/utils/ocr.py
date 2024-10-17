import os
import fitz
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import torch

def has_ocr(self):
    pdf_path = os.path.join(self.filepath, self.config.get_shared_state('current_file'))
    try:
        pdf_document = fitz.open(pdf_path)
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
    text = ''
    pdf_path = os.path.join(self.filepath, self.config.get_shared_state('current_file'))
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text()
        self.ocr_text = text
        return True
    except Exception as e:
        self.logger.error(f"An error occurred in extract_text_from_pdf_file: {e}")
        return False

def extract_text_doctr(self):
    pdf_path = os.path.join(self.filepath, self.config.get_shared_state('current_file'))
    text = ''
    try:
        if self.enable_ocr_gpu:
            self.logger.info("OCR using GPU")
            device = torch.device("cuda:0")
            model = ocr_predictor(pretrained=True).to(device)
        else:
            self.logger.info("OCR using CPU")
            model = ocr_predictor(pretrained=True)
        doc = DocumentFile.from_pdf(pdf_path)
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