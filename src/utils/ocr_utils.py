import fitz
import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

def has_ocr(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        for page in pdf_document:
            if page.get_text().strip():
                return True
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def extract_text_doctr(pdf_path, enable_ocr_gpu=True):
    try:
        if enable_ocr_gpu:
            device = torch.device("cuda:0")
            model = ocr_predictor(pretrained=True).to(device)
        else:
            model = ocr_predictor(pretrained=True)

        doc = DocumentFile.from_pdf(pdf_path)
        result = model(doc)

        text = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    text += '\n' + ' '.join(word.value for word in line.words)

        return text
    except Exception as e:
        print(f"An error occurred during OCR: {e}")
        return None


def extract_text_from_pdf_file(pdf_path):
    try:
        with fitz.open(pdf_path) as pdf_document:
            return " ".join(page.get_text() for page in pdf_document)
    except Exception as e:
        print(f"An error occurred while extracting text: {e}")
        return None
