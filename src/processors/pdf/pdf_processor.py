"""
Module for processing PDF documents in the Oscar EMR system.

This module serves as an entry point for PDF processing operations.
It imports and uses the PdfProcessor class from the pdf submodule.

Dependencies:
- utils.config_manager: For accessing configuration settings
- processors.pdf.pdf_processor: For PDF processing functionality
"""

from utils.config_manager import ConfigManager
from processors.pdf.pdf_processor import PdfProcessor

def create_pdf_processor(config: ConfigManager, session):
    """
    Create and return a PdfProcessor instance.

    Args:
        config (ConfigManager): Configuration manager containing system settings.
        session: Session object for making HTTP requests.

    Returns:
        PdfProcessor: An instance of the PdfProcessor class.
    """
    return PdfProcessor(config, session)
