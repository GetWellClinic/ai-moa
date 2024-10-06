"""
Module for processing PDF documents in the Oscar EMR system.

This module contains the PdfProcessor class which handles the retrieval
and processing of PDF documents from the Oscar EMR system.
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

    def get_pdf_content(self, name):
        """
        Fetch the content of a PDF file from the Oscar EMR system.

        Args:
            name (str): Name of the PDF file to fetch.

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

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after successful login.

        Returns:
            str: Timestamp of the last processed PDF.
        """
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.config.get('base_url')}/login.do":
            print("Login failed.")
            return self.config.get('last_processed_pdf')

        driver.get(f"{self.config.get('base_url')}/dms/incomingDocs.jsp")
        driver.execute_script("loadPdf('1', 'File');")
        driver.implicitly_wait(10)
        select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

        update_time = self.config.get('last_processed_pdf')

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

        self.config.set('last_processed_pdf', update_time)
        return update_time
