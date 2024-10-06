"""
Module for fetching PDF content from the Oscar EMR system.
"""

from utils.config_manager import ConfigManager


class PdfFetcher:
    """
    Class for fetching PDF content from the Oscar EMR system.

    Attributes:
        config (ConfigManager): Configuration manager for the system.
        session: Session object for making HTTP requests.
        base_url (str): Base URL of the EMR system.
    """

    def __init__(self, config: ConfigManager, session):
        self.config = config
        self.session = session
        self.base_url = config.get('base_url')

    def get_pdf_content(self, name):
        """
        Fetch the content of a PDF file from the Oscar EMR system.

        Args:
            name (str): Name or identifier of the PDF file to fetch.

        Returns:
            bytes: Content of the PDF file if successful, None otherwise.
        """
        pdf_url = (f"{self.base_url}/dms/ManageDocument.do?"
                   f"method=displayIncomingDocs&curPage=1&pdfDir=File&"
                   f"queue_Id=1&pdfName={name}")
        pdf_response = self.session.get(pdf_url)
        if pdf_response.status_code == 200:
            return pdf_response.content
        else:
            print(f"Failed to fetch PDF content. "
                  f"Status code: {pdf_response.status_code}")
            return None
