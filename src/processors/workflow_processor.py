"""
Module for processing workflows in the Oscar EMR system.

This module contains the WorkflowProcessor class which handles the execution
of predefined workflows within the Oscar EMR system.
"""

import logging
from utils.workflow import Workflow


class WorkflowProcessor:
    """
    Class for processing workflows in the Oscar EMR system.

    This class provides methods for executing predefined workflows
    based on the configuration settings.

    Attributes:
        config: Configuration object containing system settings.
        session_manager: SessionManager object for handling EMR sessions.
        logger: Logger instance for this class.
    """

    def __init__(self, config, session_manager):
        """
        Initialize WorkflowProcessor with configuration and session manager.

        Args:
            config: Configuration object containing system settings.
            session_manager: SessionManager object for handling EMR sessions.
        """
        self.config = config
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)

    def process_workflow(self, driver, login_url, login_successful_callback):
        """
        Process the workflow defined in the configuration.

        This method logs into the EMR system and executes the workflow
        defined in the configuration file.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after successful login.
        """
        self.logger.info("Starting workflow processing")
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.config.base_url}/login.do":
            self.logger.error("Login failed.")
            return

        workflow = Workflow(
            self.config.workflow_file_path,
            self.session_manager.get_session(),
            self.config.base_url,
            "workflow.csv",
            self.config.enable_ocr_gpu
        )
        workflow.execute_tasks_from_csv()
        self.logger.info("Workflow processing completed")
