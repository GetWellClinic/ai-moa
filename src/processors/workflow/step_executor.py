"""
Module for executing individual workflow steps in the Oscar EMR system.

This module contains the WorkflowStepExecutor class which handles the execution
of individual steps within a workflow.
"""

from utils.workflow import Workflow

class WorkflowStepExecutor:
    """
    Class for executing individual workflow steps.

    This class provides methods for executing specific steps of a workflow.

    Attributes:
        session_manager: SessionManager object for handling EMR sessions.
        config: Configuration manager containing system settings.
    """

    def __init__(self, session_manager, config):
        """
        Initialize WorkflowStepExecutor with session manager and configuration.

        Args:
            session_manager: SessionManager object for handling EMR sessions.
            config: Configuration manager containing system settings.
        """
        self.session_manager = session_manager
        self.config = config

    def execute_step(self, step_name, *args, **kwargs):
        """
        Execute a specific workflow step.

        This method creates a Workflow instance and executes the specified step.

        Args:
            step_name (str): Name of the workflow step to execute.
            *args: Variable length argument list for the step.
            **kwargs: Arbitrary keyword arguments for the step.
        """
        workflow = Workflow(self.session_manager.get_session(), self.config)
        return workflow.execute_step(step_name, *args, **kwargs)
