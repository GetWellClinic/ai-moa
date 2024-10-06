"""
Module for processing workflows in the Oscar EMR system.

This module contains the WorkflowProcessor class which handles the execution
of predefined workflows within the Oscar EMR system.
"""

from utils.workflow import Workflow

class WorkflowProcessor:
    """
    Class for processing workflows in the Oscar EMR system.

    This class provides methods for executing predefined workflows
    based on the configuration settings.

    Attributes:
        config (dict): Configuration dictionary containing system settings.
        session_manager: SessionManager object for handling EMR sessions.
    """

    def __init__(self, config, session_manager):
        """
        Initialize WorkflowProcessor with configuration and session manager.

        Args:
            config (dict): Configuration dictionary containing system settings.
            session_manager: SessionManager object for handling EMR sessions.
        """
        self.config = config
        self.session_manager = session_manager

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
        print("Starting workflow processing")
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.config['base_url']}/login.do":
            print("Login failed.")
            return

        workflow = Workflow(
            self.config.get('workflow_file_path', 'workflow.csv'),
            self.session_manager.get_session(),
            self.config['base_url'],
            "workflow.csv",
            self.config['enable_ocr_gpu']
        )
        workflow.execute_tasks_from_csv()
        print("Workflow processing completed")
