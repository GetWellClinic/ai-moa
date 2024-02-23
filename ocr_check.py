import fitz

def has_ocr(pdf_path):
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

pdf_path = "sample.pdf"

if has_ocr(pdf_path):
    print("PDF has OCR layer.")
else:
    print("PDF does not have OCR layer.")
