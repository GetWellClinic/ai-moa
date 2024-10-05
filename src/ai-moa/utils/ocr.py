import io

import fitz
import pytesseract
from PIL import Image


def extract_text_from_pdf(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        extracted_text = ''
        print(f"Number of pages: {len(pdf_document)}")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))

                image_text = pytesseract.image_to_string(image)
                extracted_text += image_text + '\n'
        return extracted_text
    except Exception as e:
        print(f"An error occurred while extracting text from PDF: {e}")
        return None


def has_ocr(pdf_path):
    try:
        with fitz.open(pdf_path) as pdf_document:
            for page in pdf_document:
                if page.get_text().strip():
                    return True
        return False
    except Exception as e:
        print(f"An error occurred while checking for OCR: {e}")
        return False
