"""
Module for processing documents in the Oscar EMR system.

This module contains the DocumentProcessor class which handles the retrieval
and processing of various documents from the Oscar EMR system.

The module provides functionality to:
1. Fetch individual document content
2. Process multiple documents in batch
3. Execute workflows on document files

Dependencies:
- utils.workflow: For executing document workflows
- utils.config_manager: For accessing configuration settings
- selenium: For web automation (implied through the use of WebDriver)
"""

from utils.config_manager import ConfigManager
from utils.workflow import Workflow


class DocumentProcessor:
    """
    Class for processing documents in the Oscar EMR system.

    This class provides methods for fetching document content, processing
    multiple documents, and executing workflows on individual document files.

    Attributes:
        config (ConfigManager): Configuration manager for the system.
        session: Session object for making HTTP requests.
        base_url (str): Base URL of the EMR system.
    """

    def __init__(self, config: ConfigManager, session):
        """
        Initialize DocumentProcessor with configuration and session.

        Args:
            config (ConfigManager): Configuration manager containing system
                                    settings.
            session: Session object for making HTTP requests.
        """
        self.config = config
        self.session = session
        self.base_url = config.get('base_url')

    def get_file_content(self, name):
        """
        Fetch the content of a document file from the Oscar EMR system.

        This method sends a GET request to retrieve the document content and
        saves it as a PDF file if successful.

        Args:
            name (str): Document name or identifier to fetch.

        Returns:
            bool: True if the file was successfully fetched and saved, False
                  otherwise.

        Note:
            The method saves the fetched document as "downloaded_pdf.pdf" in
            the current directory.
        """
        file_url = (f"{self.base_url}/dms/ManageDocument.do?"
                    f"method=display&doc_no={name}")
        file_response = self.session.get(file_url)
        if file_response.status_code == 200 and file_response.content:
            with open("downloaded_pdf.pdf", "wb") as file:
                file.write(file_response.content)
            return True
        else:
            print(f"Failed to fetch file content. "
                  f"Status code: {file_response.status_code}")
            return False

    def process_documents(self, driver, login_url, login_successful_callback):
        """
        Process all documents in the Oscar EMR system.

        This method logs into the EMR system, retrieves a list of documents,
        and processes each document that hasn't been processed before.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after
                                       successful login.

        Returns:
            str: Document number of the last processed document.

        Note:
            This method updates the 'last_pending_doc_file' configuration value
            after processing each document.
        """
        # Attempt to log in
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            return self.config.get('last_pending_doc_file')

        # Navigate to the documents page
        driver.get(f"{self.base_url}/dms/inboxManage.do?"
                   f"method=getDocumentsInQueues")
        script_value = driver.execute_script("return typeDocLab;")

        # Process each document
        for item in script_value['DOC']:
            if int(item) > int(self.config.get('last_pending_doc_file')):
                if self.get_file_content(item):
                    workflow = Workflow("downloaded_pdf.pdf",
                                        self.session, self.config)
                    workflow.execute_tasks_from_csv()
                    self.config.set('last_pending_doc_file', item)

        return self.config.get('last_pending_doc_file')
