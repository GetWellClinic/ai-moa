# COPYRIGHT © 2024 by Spring Health Corporation <office(at)springhealth.org>
# Toronto, Ontario, Canada
# SUMMARY: This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software,
# documentation, and configuration files.
# These programs, documentation, and configuration files are made available to you as open source
# in the hopes that your clinic or organization may find it useful and improve your care to the public
# by reducing administrative burden for your staff and service providers.
# NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
# and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
# LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
# Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.
# ***
# NOTICE: We hope that you will consider contributing to our common source code repository so that
# others may benefit from your shared work.
# However, if you distribute this code or serve this application to users in modified form,
# or as part of a derivative work, you are required to make your modified or derivative work
# source code available under the same herein described license.
# Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work
# source code can be acquired publicly in its latest most up-to-date version, within one month.
# ***

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
        self.workflow: Workflow = Workflow(self.config,self.session_manager,self.login_manager)

        self.logger.info("AIMOAAutomation initialized with config: %s", config_file)

    def cleanup(self) -> None:
        """
        Perform cleanup operations to release resources properly.
        """
        self.logger.info("Cleaning up resources")
        
        if hasattr(self.session_manager, 'close'):
            try:
                self.session_manager.close()
            except Exception as e:
                self.logger.exception(f"An error occurred while closing: {e}")
        else:
            self.logger.warning("The session manager does not have a close method.")

        # Close all logging handlers
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

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
def schedule_tasks() -> None:
    """
    Periodic task triggered every one minute to process workflows.
    """
    logger.info("Running scheduled tasks")
    try:
        # Accessing the environment variables
        config_file = os.getenv('CONFIG_FILE', default='../config.yaml')
        workflow_config_file = os.getenv('WORKFLOW_CONFIG_FILE', default='../workflow-config.yaml')

        with AIMOAAutomation(config_file, workflow_config_file) as ai_moa:
            ai_moa.process_workflow(ai_moa)
    except Exception as e:
        logger.exception("Error during scheduled task execution: %s", e)

    logger.info("Scheduled tasks completed")
