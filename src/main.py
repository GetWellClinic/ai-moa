"""
Main module for automating Oscar EMR tasks.

This module contains the OscarAutomation class which orchestrates the automation
of various tasks in the Oscar EMR system, including PDF processing, document
processing, and workflow execution using Huey for task management.
"""

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils.logging_setup import setup_logging
from models.login import Login
from models.session_manager import SessionManager
from processors.pdf_processor import PdfProcessor
from processors.document_processor import DocumentProcessor
from processors.workflow_processor import WorkflowProcessor
from utils.config_manager import ConfigManager
from huey import MemoryHuey
from huey.api import task, TaskLock

huey = MemoryHuey()

class OscarAutomation:
    """
    Main class for automating Oscar EMR tasks.

    This class initializes the necessary components and provides methods
    for processing PDFs, documents, and workflows using Huey for task management.

    Attributes:
        config (ConfigManager): Configuration manager instance.
        logger (logging.Logger): Logger instance for this class.
        session_manager (SessionManager): Session manager for handling EMR sessions.
        login (Login): Login handler for EMR authentication.
    """

    def __init__(self, config_file='config/config.yaml'):
        """
        Initialize OscarAutomation with configuration and necessary components.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config = ConfigManager(config_file)
        self.logger = setup_logging(self.config.config)
        self.session_manager = SessionManager(self.config)
        self.login = Login(self.config, self.session_manager)
        self.workflow_config = self.load_workflow_config()

    def _get_driver(self):
        """
        Create and configure a Chrome WebDriver instance.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance.
        """
        chrome_options = Options()
        if self.config.get('chrome_options', {}).get('headless', False):
            chrome_options.add_argument("--headless")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def load_workflow_config(self):
        """
        Load the workflow configuration from YAML file.

        Returns:
            dict: Workflow configuration.
        """
        with open('config/workflow-config.yaml', 'r') as file:
            return yaml.safe_load(file)

    @task()
    def process_pdfs(self):
        """Process PDFs using Huey task."""
        with TaskLock('pdf_processing'):
            pdf_processor = PdfProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            pdf_processor.process_pdfs(driver, f"{self.config['base_url']}/login.do", self.login.login_successful_callback)
            driver.quit()

    @task()
    def process_documents(self):
        """Process documents using Huey task."""
        with TaskLock('document_processing'):
            document_processor = DocumentProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            document_processor.process_documents(driver, f"{self.config['base_url']}/login.do", self.login.login_successful_callback)
            driver.quit()

    @task()
    def process_workflow(self):
        """Process workflow using Huey task."""
        with TaskLock('workflow_processing'):
            workflow_processor = WorkflowProcessor(self.config, self.session_manager, self.workflow_config)
            driver = self._get_driver()
            workflow_processor.process_workflow(driver, f"{self.config['base_url']}/login.do", self.login.login_successful_callback)
            driver.quit()

    @task()
    def schedule_tasks(self):
        """
        Schedule and run tasks using Huey.

        This method schedules PDF processing, document processing, and workflow processing tasks.
        """
        self.logger.info("Scheduling tasks")
        self.process_documents()
        self.process_pdfs()
        self.process_workflow()

if __name__ == "__main__":
    oscar = OscarAutomation()
    oscar.schedule_tasks()
