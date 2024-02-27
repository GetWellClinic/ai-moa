import pytesseract
from PIL import Image
import fitz
import io
import sys

def extract_text_from_pdf(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        extracted_text = ''
        print(len(pdf_document))
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
                print(image_text)
        return extracted_text
    except Exception as e:
        print("An error occurred:", e)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    extracted_text = extract_text_from_pdf(pdf_path)
    if extracted_text:
        print("Text extracted from PDF:")
        print(extracted_text)
    else:
        print("Failed to extract text from PDF.")
