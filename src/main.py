"""
Main module for automating Oscar EMR tasks.

This module contains the OscarAutomation class which orchestrates the automation
of various tasks in the Oscar EMR system, including PDF processing, document
processing, and workflow execution.
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from utils.config_manager import ConfigManager
from utils.logging_setup import setup_logging
from models.login import Login
from models.session_manager import SessionManager
from processors.pdf_processor import PdfProcessor
from processors.document_processor import DocumentProcessor
from processors.workflow_processor import WorkflowProcessor


class OscarAutomation:
    """
    Main class for automating Oscar EMR tasks.

    This class initializes the necessary components and provides methods
    for processing PDFs, documents, and workflows.

    Attributes:
        config (ConfigManager): Configuration manager instance.
        logger (logging.Logger): Logger instance for this class.
        session_manager (SessionManager): Session manager for handling EMR sessions.
        login (Login): Login handler for EMR authentication.
        ai_config (dict): AI configuration settings.
    """

    def __init__(self):
        """
        Initialize OscarAutomation with configuration and necessary components.
        """
        self.config = ConfigManager('config/config.yaml')
        setup_logging(self.config.config)
        self.logger = logging.getLogger(__name__)
        self.session_manager = SessionManager(self.config)
        self.login = Login(self.config, self.session_manager)
        self.ai_config = self.config.ai_config

    def process_pdfs(self):
        """
        Process PDF documents.

        This method initializes a PDF processor and processes PDF documents
        using the configured settings and login credentials.
        """
        self.logger.info("Starting PDF processing")
        with self._get_driver() as driver:
            pdf_processor = PdfProcessor(self.config, self.session_manager)
            self.config.last_processed_pdf = pdf_processor.process_pdfs(
                driver, self.login.login_url, self.login.login_successful_callback
            )
        self.logger.info("PDF processing completed")

    def process_documents(self):
        """
        Process general documents.

        This method initializes a document processor and processes general
        documents using the configured settings and login credentials.
        """
        self.logger.info("Starting document processing")
        with self._get_driver() as driver:
            document_processor = DocumentProcessor(self.config, self.session_manager)
            self.config.last_pending_doc_file = document_processor.process_documents(
                driver, self.login.login_url, self.login.login_successful_callback
            )
        self.logger.info("Document processing completed")

    def _get_driver(self):
        """
        Create and configure a Chrome WebDriver instance.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance.
        """
        chrome_options = Options()
        if self.config.chrome_options['headless']:
            chrome_options.add_argument("--headless")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def process_workflow(self):
        """
        Process the workflow if a workflow file path is configured.

        This method initializes a workflow processor and executes the defined
        workflow if a valid workflow file path is provided in the configuration.
        """
        if self.config.workflow_file_path:
            self.logger.info("Starting workflow processing")
            with self._get_driver() as driver:
                workflow_processor = WorkflowProcessor(self.config, self.session_manager)
                workflow_processor.process_workflow(
                    driver, self.login.login_url, self.login.login_successful_callback
                )
            self.logger.info("Workflow processing completed")
        else:
            self.logger.warning("Workflow file path is not configured. Skipping workflow processing.")


if __name__ == "__main__":
    oscar = OscarAutomation()
    oscar.process_documents()
    oscar.process_pdfs()
    oscar.process_workflow()
