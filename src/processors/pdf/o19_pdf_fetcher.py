from .base_pdf_fetcher import BasePdfFetcher

class O19PdfFetcher(BasePdfFetcher):
    """
    Fetches PDF content from the O19 EMR system.
    """

    def __init__(self, config, session):
        self.config = config
        self.session = session
        self.base_url = config.get('emr.base_url')

    def get_pdf_content(self, name):
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
