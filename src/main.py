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
from huey import MemoryHuey
from huey import crontab
from auth import LoginManager, DriverManager, SessionManager
from processors import DocumentProcessor, PdfProcessor, WorkflowProcessor, Workflow
from src.config import ConfigManager
from src.logging import setup_logging

# Initialize Huey with in-memory storage
huey = MemoryHuey('aimoa_automation')

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
        self.session_manager = SessionManager(self.config)
        self.login_manager = LoginManager(self.config)
        self.workflow = Workflow(self.config)
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
    def process_workflow(self):
        """
        Process the workflow defined in the configuration using Huey tasks.

        This method is decorated as a Huey task and handles the execution
        of the workflow defined in the configuration.
        """
        self.logger.info("Starting workflow processing task")
        self.workflow.execute_workflow()
        self.logger.info("Workflow processing task completed")

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
    ai_moa.process_workflow()
    logger.info("Scheduled tasks completed")

if __name__ == "__main__":
    logger.info("AIMOA Automation started. Waiting for scheduled tasks...")
