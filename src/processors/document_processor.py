"""
Module for processing documents in the Oscar EMR system.

This module contains the DocumentProcessor class which handles the retrieval
and processing of various documents from the Oscar EMR system.
"""

from utils.workflow import Workflow

class DocumentProcessor:
    """
    Class for processing documents in the Oscar EMR system.

    This class provides methods for fetching document content, processing
    multiple documents, and executing workflows on individual document files.

    Attributes:
        base_url (str): Base URL for the Oscar EMR system.
        session: Session object for making HTTP requests.
        last_pending_doc_file (str): Document number of the last processed document.
        enable_ocr_gpu (bool): Flag to enable GPU for OCR processing.
    """

    def __init__(self, config, session):
        """
        Initialize DocumentProcessor with configuration and session.

        Args:
            config (dict): Configuration dictionary containing system settings.
            session: Session object for making HTTP requests.
        """
        self.base_url = config['base_url']
        self.session = session
        self.last_pending_doc_file = config['last_pending_doc_file']
        self.enable_ocr_gpu = config['enable_ocr_gpu']

    def get_file_content(self, name):
        """
        Fetch the content of a document file from the Oscar EMR system.

        Args:
            name (str): Document name to fetch.

        Returns:
            bool: True if the file was successfully fetched and saved, False otherwise.
        """
        file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={name}"
        file_response = self.session.get(file_url)
        if file_response.status_code == 200 and file_response.content:
            with open("downloaded_pdf.pdf", "wb") as file:
                file.write(file_response.content)
            return True
        else:
            print(f"Failed to fetch file content. Status code: {file_response.status_code}")
            return False

    def process_documents(self, driver, login_url, login_successful_callback):
        """
        Process all documents in the Oscar EMR system.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after successful login.

        Returns:
            str: Document number of the last processed document.
        """
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            return self.last_pending_doc_file

        driver.get(f"{self.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
        script_value = driver.execute_script("return typeDocLab;")

        for item in script_value['DOC']:
            if int(item) > int(self.last_pending_doc_file):
                if self.get_file_content(item):
                    workflow = Workflow("downloaded_pdf.pdf", self.session, self.base_url, item, self.enable_ocr_gpu)
                    workflow.execute_tasks_from_csv()
                    self.last_pending_doc_file = item

        return self.last_pending_doc_file
