"""
Module for processing PDF documents in the Oscar EMR system.

This module contains the PdfProcessor class which handles the retrieval
and processing of PDF documents from the Oscar EMR system.

The module provides functionality to:
1. Fetch individual PDF content
2. Process multiple PDFs in batch
3. Execute workflows on PDF files

Dependencies:
- selenium: For web automation
- datetime: For timestamp handling
- utils.workflow: For executing PDF workflows
- utils.config_manager: For accessing configuration settings
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
from utils.workflow import Workflow
from utils.config_manager import ConfigManager

class PdfProcessor:
    """
    Class for processing PDF documents in the Oscar EMR system.

    This class provides methods for fetching PDF content, processing
    multiple PDFs, and executing workflows on individual PDF files.

    Attributes:
        config (ConfigManager): Configuration manager for the system.
        session: Session object for making HTTP requests.
        base_url (str): Base URL of the EMR system.
    """

    def __init__(self, config: ConfigManager, session):
        """
        Initialize PdfProcessor with configuration and session.

        Args:
            config (ConfigManager): Configuration manager containing system settings.
            session: Session object for making HTTP requests.
        """
        self.config = config
        self.session = session
        self.base_url = config.get('base_url')

    def get_pdf_content(self, name):
        """
        Fetch the content of a PDF file from the Oscar EMR system.

        This method sends a GET request to retrieve the PDF content.

        Args:
            name (str): Name or identifier of the PDF file to fetch.

        Returns:
            bytes: Content of the PDF file if successful, None otherwise.
        """
        pdf_url = f"{self.base_url}/dms/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir=File&queueId=1&pdfName={name}"
        pdf_response = self.session.get(pdf_url)
        if pdf_response.status_code == 200:
            return pdf_response.content
        else:
            print(f"Failed to fetch PDF content. Status code: {pdf_response.status_code}")
            return None

    def process_pdfs(self, driver, login_url, login_successful_callback):
        """
        Process all PDFs in the Oscar EMR system.

        This method logs into the EMR system, retrieves a list of PDFs,
        and processes each PDF that hasn't been processed before.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after successful login.

        Returns:
            str: Timestamp of the last processed PDF.

        Note:
            This method updates the 'last_processed_pdf' configuration value
            after processing each PDF.
        """
        # Attempt to log in
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            return self.config.get('last_processed_pdf')

        # Navigate to the PDFs page
        driver.get(f"{self.base_url}/dms/incomingDocs.jsp")
        driver.execute_script("loadPdf('1', 'File');")
        driver.implicitly_wait(10)
        select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

        update_time = self.config.get('last_processed_pdf')

        # Process each PDF
        for option in select_element.options:
            if option.get_attribute('value') != "":
                split_string = option.get_attribute('text').split(") ", 1)
                current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")
                last_file = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S") if update_time else current_file

                if last_file <= current_file:
                    update_time = split_string[1]
                    pdf_content = self.get_pdf_content(option.get_attribute('value'))
                    if pdf_content:
                        with open("downloaded_pdf.pdf", "wb") as f:
                            f.write(pdf_content)
                        workflow = Workflow("downloaded_pdf.pdf", self.session, self.config)
                        workflow.execute_tasks_from_csv()

        # Update the last processed PDF timestamp
        self.config.set('last_processed_pdf', update_time)
        return update_time
