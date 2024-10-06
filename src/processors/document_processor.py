"""
Module for processing documents in the Oscar EMR system.

This module contains the DocumentProcessor class which handles the retrieval
and processing of various documents from the Oscar EMR system.
"""

from utils.workflow import Workflow

from utils.config_manager import ConfigManager

class DocumentProcessor:
    """
    Class for processing documents in the Oscar EMR system.

    This class provides methods for fetching document content, processing
    multiple documents, and executing workflows on individual document files.

    Attributes:
        config (ConfigManager): Configuration manager for the system.
        session: Session object for making HTTP requests.
    """

    def __init__(self, config: ConfigManager, session):
        """
        Initialize DocumentProcessor with configuration and session.

        Args:
            config (ConfigManager): Configuration manager containing system settings.
            session: Session object for making HTTP requests.
        """
        self.config = config
        self.session = session

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
        if current_url == f"{self.config.get('base_url')}/login.do":
            print("Login failed.")
            return self.config.get('last_pending_doc_file')

        driver.get(f"{self.config.get('base_url')}/dms/inboxManage.do?method=getDocumentsInQueues")
        script_value = driver.execute_script("return typeDocLab;")

        for item in script_value['DOC']:
            if int(item) > int(self.config.get('last_pending_doc_file')):
                if self.get_file_content(item):
                    workflow = Workflow("downloaded_pdf.pdf", self.session, self.config)
                    workflow.execute_tasks_from_csv()
                    self.config.set('last_pending_doc_file', item)

        return self.config.get('last_pending_doc_file')
