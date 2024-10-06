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

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utils.config_manager import ConfigManager
from utils.workflow import Workflow
from auth import LoginManager, DriverManager

from .pdf_fetcher import PdfFetcher


class PdfProcessor:
    """
    Class for processing PDF documents in the Oscar EMR system.

    This class provides methods for fetching PDF content, processing
    multiple PDFs, and executing workflows on individual PDF files.

    Attributes:
        config (ConfigManager): Configuration manager for the system.
        session_manager: SessionManager object for handling EMR sessions.
        pdf_fetcher (PdfFetcher): Instance of PdfFetcher for fetching PDF
                                  content.
    """

    def __init__(self, config: ConfigManager, session_manager):
        """
        Initialize PdfProcessor with configuration and session manager.

        Args:
            config (ConfigManager): Configuration manager containing system
                                    settings.
            session_manager: SessionManager object for handling EMR sessions.
        """
        self.config = config
        self.session_manager = session_manager
        self.pdf_fetcher = PdfFetcher(config, session_manager.get_session())

    def process_pdfs(self, login_url, login_successful_callback):
        """
        Process all PDFs in the Oscar EMR system.

        Args:
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after
                                       successful login.

        Returns:
            str: Timestamp of the last processed PDF.
        """
        driver_manager = DriverManager(self.config)
        driver = driver_manager.get_driver()

        if not self._login(driver, login_url):
            driver.quit()
            return self.config.get('last_processed_pdf')

        driver.get(f"{self.config.get('base_url')}/dms/incomingDocs.jsp")
        driver.execute_script("loadPdf('1', 'File');")
        driver.implicitly_wait(10)
        select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

        update_time = self.config.get('last_processed_pdf')

        for option in select_element.options:
            if option.get_attribute('value') != "":
                update_time = self._process_pdf(option, update_time)

        self.config.set('last_processed_pdf', update_time)
        return update_time

    def _login(self, driver, login_url):
        current_url = self.login_manager.login_with_selenium(driver)
        if not self.login_manager.is_login_successful(current_url):
            print("Login failed.")
            return False
        return True

    def _process_pdf(self, option, update_time):
        split_string = option.get_attribute('text').split(") ", 1)
        current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")
        last_file = (datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
                     if update_time else current_file)

        if last_file <= current_file:
            update_time = split_string[1]
            pdf_content = self.pdf_fetcher.get_pdf_content(
                option.get_attribute('value'))
            if pdf_content:
                self._save_and_process_pdf(pdf_content)

        return update_time

    def _save_and_process_pdf(self, pdf_content):
        with open("downloaded_pdf.pdf", "wb") as f:
            f.write(pdf_content)
        workflow = Workflow("downloaded_pdf.pdf",
                            self.session_manager.get_session(), self.config)
        workflow.execute_tasks_from_csv()
