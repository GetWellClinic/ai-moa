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

import os
import io
import fitz
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import torch

def has_ocr(self):
    """
    Check if the provided PDF contains text, indicating it has OCR.

    This method checks if any of the pages in the PDF have text content, 
    which would indicate that Optical Character Recognition (OCR) has been 
    applied to the document.

    Args:
        None

    Returns:
        bool: 
            - `True` if the PDF contains any text.
            - `False` if the PDF does not contain any text or if an error occurs.

    Example:
        >>> result = has_ocr()
        >>> print(result)
        True  # If OCR is detected in the document.

    Logs:
        - Logs an error if an exception occurs during OCR detection.
    
    Raises:
        Exception: If there is an issue loading or reading the PDF.
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
    Extract text from the provided PDF bytes using the PyPDF2 library.

    This method attempts to extract text from each page of the PDF document 
    using the `PyPDF2` library. It combines the extracted text into one string.

    Args:
        None

    Returns:
        bool:
            - `True` if text extraction is successful.
            - `False` if an error occurs during extraction.

    Example:
        >>> result = extract_text_from_pdf_file()
        >>> print(result)
        True  # If the text extraction was successful.

    Logs:
        - Logs an error if an exception occurs during text extraction.
    
    Raises:
        Exception: If there is an issue reading the PDF file or extracting text.
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
    Extract text from the provided PDF bytes using OCR (Optical Character Recognition).

    This method uses the `doctr` library to perform OCR on the PDF document 
    and extract text. It can use either the CPU or GPU depending on configuration.

    Args:
        None

    Returns:
        bool:
            - `True` if text extraction is successful using OCR.
            - `False` if an error occurs during OCR extraction.

    Example:
        >>> result = extract_text_doctr()
        >>> print(result)
        True  # If the OCR text extraction was successful.

    Logs:
        - Logs the start and completion of the OCR process.
        - Logs an error if an exception occurs during OCR processing.
    
    Raises:
        Exception: If there is an issue performing OCR or reading the PDF.
    """
    text = ''
    try:
        if self.enable_ocr_gpu:
            self.logger.debug("OCR using GPU")
            device = torch.device(self.config.get('ocr.device'))
            model = ocr_predictor(pretrained=True).to(device)
        else:
            self.logger.debug("OCR using CPU")
            model = ocr_predictor(pretrained=True)
        
        # Read the PDF from bytes (or file)
        pdf_bytes = self.config.get_shared_state('current_file')
        pdf_io = io.BytesIO(pdf_bytes)

        # Read the entire PDF into a list of pages
        doc = DocumentFile.from_pdf(pdf_io)

        # Truncate the pages to a limit (page_limit)
        page_limit = self.config.get('ocr.page_limit')
        self.logger.debug(f"OCR page limit: {page_limit}")

        # Truncate the document before passing to the model
        truncated_doc = doc[:page_limit]  # Limit the number of pages

        # Now perform OCR on the truncated document
        self.logger.debug("OCR started.")
        result = model(truncated_doc)

        # Process the OCR result
        text = ""
        for page_index, page in enumerate(result.pages):
            self.logger.debug(f"OCR processing page number: {page_index}")
            for block in page.blocks:
                for line in block.lines:
                    text += '\n'
                    for word in line.words:
                        text += word.value + ' '

        self.ocr_text = text
        self.logger.debug("OCR completed.")
        return True
    except Exception as e:
        self.logger.error(f"An error occurred in extract_text_doctr: {e}")
        return False