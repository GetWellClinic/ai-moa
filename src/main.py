"""
Main module for automating Oscar EMR tasks.

This module contains the OscarAutomation class which orchestrates the automation
of various tasks in the Oscar EMR system, including PDF processing, document
processing, and workflow execution using Huey for task management.

The module uses several components:
- ConfigManager and WorkflowConfigManager for handling configurations
- SessionManager for managing EMR sessions
- Login for handling EMR authentication
- PdfProcessor, DocumentProcessor, and WorkflowProcessor for specific task processing
- Huey for task queue management

The main class, OscarAutomation, initializes these components and provides methods
for processing PDFs, documents, and workflows as Huey tasks.
"""

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils.logging_setup import setup_logging
from models.login import Login
from models.session_manager import SessionManager
from processors.pdf.pdf_processor import PdfProcessor
from processors.document_processor import DocumentProcessor
from processors.workflow.processor import WorkflowProcessor
from utils.config_manager import ConfigManager, WorkflowConfigManager
from huey import RedisHuey
from huey.api import task, TaskLock

class OscarAutomation:
    """
    Main class for automating Oscar EMR tasks.

    This class initializes the necessary components and provides methods
    for processing PDFs, documents, and workflows using Huey for task management.

    Attributes:
        config (ConfigManager): Configuration manager instance for general settings.
        workflow_config (WorkflowConfigManager): Configuration manager instance for workflow settings.
        logger (logging.Logger): Logger instance for this class.
        session_manager (SessionManager): Session manager for handling EMR sessions.
        login (Login): Login handler for EMR authentication.
        huey (RedisHuey): Huey instance for task management.
    """

    def __init__(self, config_file='config/config.yaml', workflow_config_file='config/config-workflow.yaml'):
        """
        Initialize OscarAutomation with configuration and necessary components.

        This method sets up the configuration managers, logger, session manager, login handler,
        and Huey task queue.

        Args:
            config_file (str): Path to the main configuration file.
            workflow_config_file (str): Path to the workflow configuration file.
        """
        self.config = ConfigManager(config_file)
        self.workflow_config = WorkflowConfigManager(workflow_config_file)
        self.logger = setup_logging(self.config.config)
        self.session_manager = SessionManager(self.config)
        self.login = Login(self.config, self.session_manager)
        self.huey = self.setup_huey()

    def _get_driver(self):
        """
        Create and configure a Chrome WebDriver instance.

        This method sets up a Chrome WebDriver with options specified in the configuration.
        It uses the webdriver_manager to automatically manage the ChromeDriver binary.

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

    def setup_huey(self):
        """
        Set up Huey instance based on configuration.

        This method configures a RedisHuey instance using settings from the configuration.
        It sets up the task queue name, Redis connection details, and other Huey-specific options.

        Returns:
            RedisHuey: Configured Huey instance for task management.
        """
        huey_config = self.config.get('huey', {})
        return RedisHuey(
            huey_config.get('name', 'workflow_queue'),
            host=huey_config.get('connection', {}).get('host', 'localhost'),
            port=huey_config.get('connection', {}).get('port', 6379),
            results=huey_config.get('results', True),
            store_none=huey_config.get('store_none', False)
        )

    @task()
    def process_pdfs(self):
        """
        Process PDFs using Huey task.

        This method is decorated as a Huey task. It creates a PdfProcessor instance,
        sets up a WebDriver, and processes PDFs. The TaskLock ensures that only one
        instance of this task runs at a time.
        """
        with TaskLock('pdf_processing'):
            pdf_processor = PdfProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            pdf_processor.process_pdfs(driver, f"{self.config['base_url']}/login.do", self.login.login_successful_callback)
            driver.quit()

    @task()
    def process_documents(self):
        """
        Process documents using Huey task.

        This method is decorated as a Huey task. It creates a DocumentProcessor instance,
        sets up a WebDriver, and processes documents. The TaskLock ensures that only one
        instance of this task runs at a time.
        """
        with TaskLock('document_processing'):
            document_processor = DocumentProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            document_processor.process_documents(driver, f"{self.config['base_url']}/login.do", self.login.login_successful_callback)
            driver.quit()

    @task()
    def process_workflow(self):
        """
        Process workflow using Huey task.

        This method is decorated as a Huey task. It creates a WorkflowProcessor instance,
        sets up a WebDriver, and processes the workflow. The TaskLock ensures that only one
        instance of this task runs at a time.
        """
        with TaskLock('workflow_processing'):
            workflow_processor = WorkflowProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            workflow_processor.process_workflow(driver, f"{self.config['base_url']}/login.do", self.login.login_successful_callback)
            driver.quit()

    @task()
    def schedule_tasks(self):
        """
        Schedule and run tasks using Huey.

        This method is the main entry point for task scheduling. It schedules the document processing,
        PDF processing, and workflow processing tasks. Each task is added to the Huey task queue
        for asynchronous execution.
        """
        self.logger.info("Scheduling tasks")
        self.process_documents()
        self.process_pdfs()
        self.process_workflow()

if __name__ == "__main__":
    # Create an instance of OscarAutomation and schedule tasks
    oscar = OscarAutomation()
    oscar.schedule_tasks()
