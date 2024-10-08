# COPYRIGHT © 2024 by Spring Health Corporation <office(at)springhealth.org>
# Toronto, Ontario, Canada
# SUMMARY: This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software,
# documentation, and configuration files.
# These programs, documentation, and configuration files are made available to you as open source
# in the hopes that your clinic or organization may find it useful and improve your care to the public
# by reducing administrative burden for your staff and service providers. 
# NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
# and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
# LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
# Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.
# ***
# NOTICE: We hope that you will consider contributing to our common source code repository so that
# others may benefit from your shared work.
# However, if you distribute this code or serve this application to users in modified form,
# or as part of a derivative work, you are required to make your modified or derivative work
# source code available under the same herein described license.
# Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work
# source code can be acquired publicly in its latest most up-to-date version, within one month.
# ***

import io
import logging
import sys

import fitz
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

from config import ConfigManager

def extract_text_from_bytes(pdf_bytes, config: ConfigManager):
    enable_ocr_gpu = config.get('general.enable_ocr_gpu', False)
    tesseract_path = config.get('general.ocr.tesseract_path', '/usr/bin/tesseract')
    
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        extracted_text = ''
        logger.info(f"Processing PDF with {len(pdf_document)} pages")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))

                if enable_ocr_gpu:
                    # Use GPU-enabled OCR logic here
                    pass
                else:
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                    image_text = pytesseract.image_to_string(image)
                
                extracted_text += image_text + '\n'
                logger.debug(f"Extracted text from image {img_index} on page {page_num}")
        return extracted_text
    except Exception as e:
        logger.exception(f"An error occurred while extracting text: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 2:
        logger.error("Usage: python script_name.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    extracted_text = extract_text_from_bytes(pdf_bytes)
    if extracted_text:
        logger.info("Text extracted from PDF:")
        print(extracted_text)
    else:
        logger.error("Failed to extract text from PDF.")
