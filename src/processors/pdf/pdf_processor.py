"""
Copyright (C) 2024 Spring Health Corporation

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
from src.config import ConfigManager
from src.logging import setup_logging
from utils.workflow import Workflow
from auth import LoginManager, DriverManager

from .pdf_fetcher import PdfFetcher
from .ocr import extract_text_from_pdf


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
        self.logger = setup_logging()
        self.login_manager = LoginManager(config)

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
        driver.quit()
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
        temp_pdf_name = self.config.get('file_processing.temp_pdf_name', 'downloaded_pdf.pdf')
        with open(temp_pdf_name, "wb") as f:
            f.write(pdf_content)
        temp_pdf_name = self.config.get('file_processing.temp_pdf_name', 'downloaded_pdf.pdf')
        extracted_text = extract_text_from_pdf(temp_pdf_name)
        if extracted_text:
            workflow = Workflow(extracted_text,
                                self.session_manager.get_session(), self.config)
            workflow.execute_tasks_from_csv()
        else:
            print("Failed to extract text from PDF")

    def get_pdf_content(self, name):
        """
        Fetch the content of a PDF file from the Oscar EMR system.

        Args:
            name (str): PDF name or identifier to fetch.

        Returns:
            bytes: Content of the PDF file if successful, None otherwise.
        """
        return self.pdf_fetcher.get_pdf_content(name)
