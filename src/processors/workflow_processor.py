"""
Module for processing workflows in the Oscar EMR system using Huey tasks.

This module contains the WorkflowProcessor class which handles the execution
of predefined workflows within the Oscar EMR system using Huey for task management.
"""

from utils.workflow import Workflow
from utils.config_manager import ConfigManager
from huey import crontab
from huey.api import task, TaskLock

class WorkflowProcessor:
    """
    Class for processing workflows in the Oscar EMR system using Huey tasks.

    This class provides methods for executing predefined workflows
    based on the configuration settings using Huey for task management.

    Attributes:
        config (ConfigManager): Configuration manager containing system settings.
        session_manager: SessionManager object for handling EMR sessions.
        workflow_config: Workflow configuration loaded from YAML.
    """

    def __init__(self, config: ConfigManager, session_manager, workflow_config):
        """
        Initialize WorkflowProcessor with configuration, session manager, and workflow config.

        Args:
            config (ConfigManager): Configuration manager containing system settings.
            session_manager: SessionManager object for handling EMR sessions.
            workflow_config: Workflow configuration loaded from YAML.
        """
        self.config = config
        self.session_manager = session_manager
        self.workflow_config = workflow_config

    @task()
    def process_workflow(self, driver, login_url, login_successful_callback):
        """
        Process the workflow defined in the configuration using Huey tasks.

        This method logs into the EMR system and executes the workflow
        defined in the workflow configuration using Huey tasks.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after successful login.
        """
        with TaskLock('workflow_processing'):
            print("Starting workflow processing")
            driver.get(login_url)
            current_url = login_successful_callback(driver)
            if current_url == f"{self.config['base_url']}/login.do":
                print("Login failed.")
                return

            workflow = Workflow(self.workflow_config, self.session_manager.get_session(), self.config)
            workflow.execute_workflow()
            print("Workflow processing completed")

    @task()
    def execute_workflow_step(self, step_name, *args, **kwargs):
        """
        Execute a specific workflow step as a Huey task.

        Args:
            step_name (str): Name of the workflow step to execute.
            *args: Variable length argument list for the step.
            **kwargs: Arbitrary keyword arguments for the step.
        """
        with TaskLock(f'workflow_step_{step_name}'):
            workflow = Workflow(self.workflow_config, self.session_manager.get_session(), self.config)
            workflow.execute_step(step_name, *args, **kwargs)
