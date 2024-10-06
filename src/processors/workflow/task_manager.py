"""
Module for managing Huey tasks related to workflow processing.

This module contains the WorkflowTaskManager class which handles the creation
and management of Huey tasks for workflow processing.
"""

from huey.api import task, TaskLock

class WorkflowTaskManager:
    """
    Class for managing Huey tasks related to workflow processing.

    This class provides methods for creating and executing Huey tasks
    for workflow processing and step execution.
    """

    @task()
    def process_workflow_task(self, process_func, *args, **kwargs):
        """
        Create and execute a Huey task for processing a workflow.

        This method uses a TaskLock to ensure that only one instance
        of the workflow is running at a time.

        Args:
            process_func: Function to execute for processing the workflow.
            *args: Variable length argument list for the process function.
            **kwargs: Arbitrary keyword arguments for the process function.
        """
        with TaskLock('workflow_processing'):
            return process_func(*args, **kwargs)

    @task()
    def execute_workflow_step_task(self, execute_func, step_name, *args, **kwargs):
        """
        Create and execute a Huey task for a specific workflow step.

        This method uses a TaskLock to prevent concurrent execution of the same step.

        Args:
            execute_func: Function to execute for the workflow step.
            step_name (str): Name of the workflow step to execute.
            *args: Variable length argument list for the execute function.
            **kwargs: Arbitrary keyword arguments for the execute function.
        """
        with TaskLock(f'workflow_step_{step_name}'):
            return execute_func(step_name, *args, **kwargs)
