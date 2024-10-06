"""
Main module for automating Oscar EMR tasks using Huey for task management.

This module contains the OscarAutomation class which orchestrates the automation
of various tasks in the Oscar EMR system, including PDF processing, document
processing, and workflow execution using Huey for task management.

The module uses several components:
- ConfigManager for handling configurations
- SessionManager for managing EMR sessions
- Login for handling EMR authentication
- PdfProcessor, DocumentProcessor, and WorkflowProcessor for specific task processing
- Huey for task queue management (memory-only method)
"""

from huey import MemoryHuey
from huey.api import task, TaskLock
from auth import LoginManager, DriverManager, SessionManager
from auth import LoginManager
from processors.document_processor import DocumentProcessor
from processors.pdf.pdf_processor import PdfProcessor
from processors.workflow.processor import WorkflowProcessor
from config import ConfigManager
from utils.logging_setup import setup_logging


class OscarAutomation:
    """
    Main class for automating Oscar EMR tasks.

    This class initializes the necessary components and provides methods
    for processing PDFs, documents, and workflows using Huey for task management.

    Attributes:
        config (ConfigManager): Configuration manager instance for all settings.
        logger (logging.Logger): Logger instance for this class.
        session_manager (SessionManager): Session manager for handling EMR sessions.
        login (Login): Login handler for EMR authentication.
        huey (MemoryHuey): Huey instance for task management (memory-only).
    """

    def __init__(self, config_file='config/workflow-config.yaml'):
        """
        Initialize OscarAutomation with configuration and necessary components.

        This method sets up the configuration manager, logger, session manager,
        login handler, and Huey task queue.

        Args:
            config_file (str): Path to the workflow configuration file.
        """
        self.config = ConfigManager(config_file)
        self.logger = setup_logging(self.config.config)
        self.session_manager = SessionManager(self.config)
        self.login_manager = LoginManager(self.config)
        self.huey = self.setup_huey()

    def _get_driver(self):
        """
        Get a configured Chrome WebDriver instance.

        This method uses the DriverManager to create and configure a
        Chrome WebDriver instance.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance.
        """
        driver_manager = DriverManager(self.config)
        return driver_manager.get_driver()

    def setup_huey(self):
        """
        Set up Huey instance based on configuration.

        This method configures a MemoryHuey instance using settings from the
        configuration. It sets up the task queue name and other Huey-specific options.

        Returns:
            MemoryHuey: Configured Huey instance for task management (memory-only).
        """
        huey_config = self.config.get('huey', {})
        return MemoryHuey(
            name=huey_config.get('name', 'workflow_queue'),
            results=huey_config.get('results', True),
            store_none=huey_config.get('store_none', False),
            always_eager=huey_config.get('always_eager', True)
        )

    @task()
    def process_pdfs(self):
        """
        Process PDFs using Huey task.

        This method is decorated as a Huey task. It creates a PdfProcessor
        instance, sets up a WebDriver, and processes PDFs. The TaskLock ensures
        that only one instance of this task runs at a time.
        """
        with TaskLock('pdf_processing'):
            pdf_processor = PdfProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            pdf_processor.process_pdfs(
                driver,
                f"{self.config.get('emr', {}).get('base_url')}/login.do",
                self.login.login_successful_callback
            )
            driver.quit()

    @task()
    def process_documents(self):
        """
        Process documents using Huey task.

        This method is decorated as a Huey task. It creates a DocumentProcessor
        instance, sets up a WebDriver, and processes documents. The TaskLock
        ensures that only one instance of this task runs at a time.
        """
        with TaskLock('document_processing'):
            document_processor = DocumentProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            document_processor.process_documents(
                driver,
                f"{self.config.get('emr', {}).get('base_url')}/login.do",
                self.login.login_successful_callback
            )
            driver.quit()

    @task()
    def process_workflow(self):
        """
        Process workflow using Huey task.

        This method is decorated as a Huey task. It creates a WorkflowProcessor
        instance, sets up a WebDriver, and processes the workflow. The TaskLock
        ensures that only one instance of this task runs at a time.
        """
        with TaskLock('workflow_processing'):
            workflow_processor = WorkflowProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            workflow_processor.process_workflow(
                driver,
                f"{self.config.get('emr', {}).get('base_url')}/login.do",
                self.login.login_successful_callback
            )
            driver.quit()

    @task()
    def schedule_tasks(self):
        """
        Schedule and run tasks using Huey.

        This method is the main entry point for task scheduling. It schedules
        the document processing, PDF processing, and workflow processing tasks.
        Each task is added to the Huey task queue for execution.
        """
        self.logger.info("Scheduling tasks")
        self.process_documents()
        self.process_pdfs()
        self.process_workflow()


if __name__ == "__main__":
    # Create an instance of OscarAutomation and schedule tasks
    oscar = OscarAutomation()
    oscar.schedule_tasks()
