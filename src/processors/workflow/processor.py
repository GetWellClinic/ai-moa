from ai_moa_utils import setup_logging
from config import ConfigManager
from .emr_workflow import Workflow

from .step_executor import WorkflowStepExecutor
from .task_manager import WorkflowTaskManager
from auth import LoginManager, DriverManager


class WorkflowProcessor:
    """
    Class for processing workflows in the AI MOA system using Huey tasks.

    This class provides methods for executing predefined workflows
    based on the configuration settings using Huey for task management.

    Attributes:
        config (ConfigManager): Configuration manager containing all settings.
        session_manager: SessionManager object for handling EMR sessions.
        task_manager (WorkflowTaskManager): Manager for Huey tasks.
        step_executor (WorkflowStepExecutor): Executor for individual workflow steps.
    """

    def __init__(self, config: ConfigManager, session_manager):
        """
        Initialize WorkflowProcessor with configuration and session manager.

        Args:
            config (ConfigManager): Configuration manager containing all settings.
            session_manager: SessionManager object for handling EMR sessions.
        """
        self.config = config
        self.session_manager = session_manager
        self.task_manager = WorkflowTaskManager()
        self.step_executor = WorkflowStepExecutor(session_manager, config)

    def process_workflow(self, login_url, login_successful_callback):
        """
        Process the workflow defined in the configuration using Huey tasks.

        This method logs into the EMR system and executes the workflow
        defined in the configuration.

        Args:
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after successful login.
        """
        return self.task_manager.process_workflow_task(
            self._process_workflow_internal,
            login_url,
            login_successful_callback
        )

    def _process_workflow_internal(self, login_url, login_successful_callback):
        """
        Internal method to process the workflow.

        This method is called by the task manager and performs the actual workflow processing.

        Args:
            login_url (str): URL for logging into the EMR system.
            login_successful_callback: Callback function to execute after successful login.
        """
        print("Starting workflow processing")
        driver_manager = DriverManager(self.config)
        driver = driver_manager.get_driver()

        login_manager = LoginManager(self.config)
        current_url = login_manager.login_with_selenium(driver)
        if not login_manager.is_login_successful(current_url):
            print("Login failed.")
            return

        workflow = Workflow(self.session_manager.get_session(), self.config)
        workflow.execute_workflow()
        print("Workflow processing completed")

    def execute_workflow_step(self, step_name, *args, **kwargs):
        """
        Execute a specific workflow step as a Huey task.

        This method allows individual steps of a workflow to be executed as separate tasks.

        Args:
            step_name (str): Name of the workflow step to execute.
            *args: Variable length argument list for the step.
            **kwargs: Arbitrary keyword arguments for the step.
        """
        return self.task_manager.execute_workflow_step_task(
            self.step_executor.execute_step,
            step_name,
            *args,
            **kwargs
        )
"""
Module for processing workflows in the AI MOA system using Huey tasks.

This module contains the WorkflowProcessor class which handles the execution
of predefined workflows within the AI MOA system using Huey for task management.
"""

