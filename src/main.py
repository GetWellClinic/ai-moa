"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
"""
import logging
import os
import argparse
import signal
import sys
import time
from huey import MemoryHuey, crontab
from config import ConfigManager
from auth import LoginManager, SessionManager
from processors import Workflow
from ai_moa_utils.logging_setup import setup_logging
from datetime import datetime
from threading import Event
from typing import Optional

# Initialize a Huey instance with in-memory storage for managing asynchronous tasks.
huey: MemoryHuey = MemoryHuey('aimoa_automation')

logger: logging.Logger = logging.getLogger(__name__)
shutdown_event: Event = Event()


def check_config_files_exist(config_file: str, workflow_config_file: str) -> None:
    """
    Check if the required configuration files exist at the specified paths.
    Raises a FileNotFoundError if any of the files are missing.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file '{config_file}' is missing.")
    if not os.path.exists(workflow_config_file):
        raise FileNotFoundError(f"Workflow configuration file '{workflow_config_file}' is missing.")

    logger.info("Configuration files exist: '%s' and '%s'", config_file, workflow_config_file)


class AIMOAAutomation:
    """
    Main class for automating tasks in the AI-MOA system.
    Handles the processing of workflows and documents.
    """

    def __init__(self, config_file: str, workflow_config_file: str) -> None:
        """
        Initialize the AIMOAAutomation instance with the provided configuration files.
        """
        self.config: ConfigManager = ConfigManager(config_file, workflow_config_file)
        setup_logging(self.config)
        self.logger: logging.Logger = logger
        self.session_manager: SessionManager = SessionManager(self.config)
        self.login_manager: LoginManager = LoginManager(self.config)
        self.workflow: Workflow = Workflow(self.config)

        self.logger.info("AIMOAAutomation initialized with config: %s", config_file)

    def cleanup(self) -> None:
        """
        Perform cleanup operations to release resources properly.
        """
        self.logger.info("Cleaning up resources")
        self.session_manager.close()
        self.logger.info("Cleanup complete.")

    def __enter__(self) -> 'AIMOAAutomation':
        """
        Enter method for context management.
        """
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[BaseException],
                 traceback: Optional[object]) -> None:
        """
        Exit method for context management. Ensures cleanup is called.
        """
        self.cleanup()

    @huey.task(expires=1800, retries=3, retry_delay=10)
    def process_workflow(self) -> None:
        """
        Process the workflow as a Huey task.
        Task expires after 30 minutes and retries up to 3 times.
        """
        start_time: datetime = datetime.now()
        self.logger.info("Starting workflow task at %s", start_time.isoformat())

        try:
            self.workflow.execute_workflow()
        except Exception as e:
            self.logger.exception("An unexpected error occurred: %s", e)
            raise
        finally:
            self.cleanup()

        end_time: datetime = datetime.now()
        duration: float = (end_time - start_time).total_seconds()
        if duration > 1800:
            self.logger.warning("Workflow task expired before completion.")
        else:
            self.logger.info("Workflow task completed successfully. Duration: %s seconds", duration)


@huey.periodic_task(crontab(minute='*/5'))
def schedule_tasks(config_file: str, workflow_config_file: str) -> None:
    """
    Periodic task triggered every 5 minutes to process workflows.
    """
    logger.info("Running scheduled tasks")
    try:
        with AIMOAAutomation(config_file=config_file, workflow_config_file=workflow_config_file) as ai_moa:
            ai_moa.process_workflow()
    except Exception as e:
        logger.exception("Error during scheduled task execution: %s", e)

    logger.info("Scheduled tasks completed")


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments to allow specifying custom paths for configuration files.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Run AI-MOA Automation with optional configuration file paths.")
    parser.add_argument('--config-file', type=str, default='config.yaml', help="Path to the main configuration file")
    parser.add_argument('--workflow-config-file', type=str, default='workflow-config.yaml',
                        help="Path to the workflow configuration file")
    return parser.parse_args()


def handle_shutdown_signal(signal_number: int, frame: Optional[object]) -> None:
    """
    Handle shutdown signals to stop the Huey consumer gracefully.
    """
    logger.info(f"Received shutdown signal ({signal_number}). Stopping Huey consumer...")
    shutdown_event.set()


def start_huey_consumer(config_file: str, workflow_config_file: str, timeout: int = 60) -> None:
    """
    Programmatically start the Huey consumer, handling retries and graceful shutdown.
    Wait for tasks to complete with a maximum timeout during shutdown.
    """
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    check_config_files_exist(config_file, workflow_config_file)
    logger.info("Starting the Huey consumer...")

    retries: int = 0
    max_retries: int = 5

    while not shutdown_event.is_set() and retries < max_retries:
        try:
            huey.start()
            time.sleep(1)
        except Exception as e:
            retries += 1
            logger.exception(f"Error in Huey consumer loop (attempt {retries}/{max_retries}): %s", e)
            time.sleep(5 * (2 ** retries))  # Exponential backoff for retries

        if retries >= max_retries:
            logger.error(f"Huey consumer failed to start after {max_retries} attempts. Exiting.")
            raise RuntimeError(f"Huey consumer could not start after {max_retries} retries.")

    logger.info("Huey consumer shutting down. Waiting for running tasks to complete (max timeout: %s seconds)...",
                timeout)

    # Attempt graceful shutdown with timeout
    huey.stop(graceful=True, timeout=timeout)

    if shutdown_event.is_set():
        logger.info("Shutdown event detected. Graceful shutdown complete.")
    else:
        logger.warning("Graceful shutdown timed out after %s seconds. Forcing shutdown.", timeout)

    logger.info("Huey consumer has stopped.")


if __name__ == "__main__":
    try:
        args: argparse.Namespace = parse_args()
        logger.info("AIMOA Automation started. Waiting for scheduled tasks...")
        start_huey_consumer(args.config_file, args.workflow_config_file)
    except FileNotFoundError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.exception("An unexpected error occurred during startup: %s", e)
        raise
