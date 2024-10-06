"""
Main module for automating AI-MOA tasks using Huey for task management.

This module initializes the AIMOAAuthomation class and sets up periodic tasks
for processing documents, PDFs, and workflows in the AI MOA system.

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
"""

import os
import logging
from huey.contrib.sqlitedb import SqliteHuey
from huey import crontab
from src.auth import LoginManager, DriverManager, SessionManager
from src.processors.document import DocumentProcessor
from src.processors.pdf import PdfProcessor
from src.processors.workflow import WorkflowProcessor, Workflow
from src.config import ConfigManager
from src.logging import setup_logging

# Initialize Huey with SQLite backend
huey = SqliteHuey('aimoa_automation', filename='/app/aimoa_tasks.db')

logger = logging.getLogger(__name__)

class AIMOAAutomation:
    """
    Main class for automating tasks with the AI-MOA system.

    This class initializes the necessary components and provides methods
    for processing PDFs, documents, workflows, and files.

    Attributes:
        config (ConfigManager): Configuration manager for the application.
        logger: Logger instance for the application.
        session_manager (SessionManager): Manager for EMR sessions.
        login_manager (LoginManager): Manager for EMR login.
    """

    def __init__(self, config_file='config.yaml'):
        """
        Initialize the AIMOAAAutomation instance.

        Args:
            config_file (str): Path to the main configuration file.
        """
        self.config = ConfigManager(config_file, 'workflow-config.yaml')
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        self.session_manager = SessionManager(self.config
        self.login_manager = LoginManager(self.config)
        self.logger.info("AIMOAAutomation initialized")

    def _get_driver(self):
        """
        Get a new instance of the WebDriver.

        Returns:
            WebDriver: A new instance of the configured WebDriver.
        """
        self.logger.debug("Getting new WebDriver instance")
        driver_manager = DriverManager(self.config)
        return driver_manager.get_driver()

    @huey.task()
    def process_pdfs(self):
        """
        Process PDF documents in the EMR system.

        This method is decorated as a Huey task and handles the processing
        of PDF documents, including login and cleanup.
        """
        self.logger.info("Starting PDF processing task")
        pdf_processor = PdfProcessor(self.config, self.session_manager)
        driver = self._get_driver()
        pdf_processor.process_pdfs(
            f"{self.config.get('emr', {}).get('base_url')}/login.do",
            self.login_manager.login_successful_callback
        )
        driver.quit()
        self.logger.info("PDF processing task completed")

    @huey.task()
    def process_documents(self):
        """
        Process general documents in the EMR system.

        This method is decorated as a Huey task and handles the processing
        of general documents, including login and cleanup.
        """
        self.logger.info("Starting document processing task")
        document_processor = DocumentProcessor(self.config, self.session_manager)
        driver = self._get_driver()
        document_processor.process_documents(
            f"{self.config.get('emr', {}).get('base_url')}/login.do",
            self.login_manager.login_successful_callback
        )
        driver.quit()
        self.logger.info("Document processing task completed")

    @huey.task()
    def process_workflow(self):
        """
        Execute the main workflow in the EMR system.

        This method is decorated as a Huey task and handles the execution
        of the main workflow, including login and cleanup.
        """
        self.logger.info("Starting workflow processing task")
        workflow_processor = WorkflowProcessor(self.config, self.session_manager)
        driver = self._get_driver()
        workflow_processor.process_workflow(
            f"{self.config.get('emr', {}).get('base_url')}/login.do",
            self.login_manager.login_successful_callback
        )
        driver.quit()
        self.logger.info("Workflow processing task completed")

    @huey.task()
    def process_files(self):
        """
        Process files in the input directory.

        This method is decorated as a Huey task and handles the processing
        of files in the configured input directory, executing workflows
        for each file with an allowed extension.
        """
        self.logger.info("Starting file processing task")
        input_directory = self.config.get('file_processing', {}).get('input_directory')
        allowed_extensions = self.config.get('file_processing', {}).get('allowed_extensions')
        
        for file_name in os.listdir(input_directory):
            if any(file_name.endswith(ext) for ext in allowed_extensions):
                self.logger.debug(f"Processing file: {file_name}")
                file_path = os.path.join(input_directory, file_name)
                workflow = Workflow(self.config)
                workflow.filepath = file_path
                workflow.file_name = file_name
                workflow.execute_workflow()
        self.logger.info("File processing task completed")

@huey.periodic_task(crontab(minute=ConfigManager('src/config.yaml').get('huey.schedule.minute', '*/5')))
def schedule_tasks():
    """
    Periodic task to schedule and execute various EMR processing tasks.

    This function is decorated as a Huey periodic task and runs at intervals
    specified in the configuration. It initializes an AIMOAAutomation instance
    and triggers the processing of documents, PDFs, workflows, and files.
    """
    logger.info("Starting scheduled tasks")
    ai_moa = AIMOAAutomation()
    ai_moa.process_documents()
    ai_moa.process_pdfs()
    ai_moa.process_workflow()
    ai_moa.process_files()
    logger.info("Scheduled tasks completed")

if __name__ == "__main__":
    logger.info("AIMOA Automation started. Waiting for scheduled tasks...")
