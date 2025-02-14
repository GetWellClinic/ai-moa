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
import threading
import os
from huey import MemoryHuey, crontab
from huey.consumer import Consumer
from config import ConfigManager
from auth import LoginManager, SessionManager
from processors import Workflow
from ai_moa_utils.logging_setup import setup_logging
from datetime import datetime
from threading import Event
from typing import Optional

print("AI-MOA version 1.1; licensed under AGPL3.0, see LICENSE file. (c) Spring Health Corporation")
print("")
print("Starting AI-MOA...")
print("...waiting for Huey task scheduler to start interval...")

# Initialize a Huey instance with in-memory storage for managing asynchronous tasks.
huey: MemoryHuey = MemoryHuey('aimoa_automation')

logger: logging.Logger = logging.getLogger(__name__)
shutdown_event: Event = Event()
run_immediately: bool = False

def check_config_files_exist(config_file: str, workflow_config_file: str) -> None:
    """
    Check if the required configuration files exist at the specified paths.
    Raises a FileNotFoundError if any of the files are missing.
    """
    for file_path, file_type in [(config_file, "Configuration"), (workflow_config_file, "Workflow configuration")]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_type} file '{file_path}' is missing.")
        logger.info(f"{file_type} file exists: '{file_path}'")


class AIMOAAutomation:
    """
    Main class for automating tasks in the AI-MOA system.
    Handles the processing of workflows and documents.
    """

    def __init__(self, config_file: str, workflow_config_file: str, reset_lock: bool) -> None:
        """
        Initialize the AIMOAAutomation instance with the provided configuration files.
        """
        self.config: ConfigManager = ConfigManager(config_file, workflow_config_file)
        setup_logging(self.config)
        self.logger: logging.Logger = logger

        if reset_lock and self.config.get('lock.status'):
            self.config.update_lock_status(False)
            self.logger.info(f"Lock set to False, --reset-lock was used while starting the application.")

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

    def process_workflow(self) -> None:
        """
        Process the workflow.
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
        self.logger.info("Workflow task completed. Duration: %s seconds", duration)

@huey.task(expires=1, retries=3, retry_delay=10)
def process_workflow_task(config_file: str, workflow_config_file: str, reset_lock: bool) -> None:
    """
    Process the workflow as a Huey task.
    In this workflow setup, if Task does not start, it is removed from Huey queu after 1 second, and retries up to 3 times.
    If the Task is set to cron repeat every 1 minute, expiring a waiting task in queu prevents duplicate tasks being placed in Huey queu if the previous task is not completed, and allows for faster processing when enqueing attempts occur at every 1 minute intervals.
    """
    with AIMOAAutomation(config_file, workflow_config_file, reset_lock) as ai_moa:
        ai_moa.process_workflow()

def args_parse_aimoa():
    """
    Parses command-line arguments for AI-MOA automation.

    This function sets up an argument parser and returns the parsed arguments.
    It supports the following arguments:
        --config: Path to the configuration file.
        --workflow-config: Path to the workflow configuration file.
        --cron-interval: Cron interval for scheduling tasks (e.g., '*/5' for every 5 minutes).
        --run-immediately: If set, the task will run immediately when started.

    Returns:
        argparse.Namespace: The parsed arguments as an object with attributes corresponding
                            to the command-line arguments.
    """
    parser = argparse.ArgumentParser(description="AI-MOA Automation")
    parser.add_argument("--config", help="Path to the config file")
    parser.add_argument("--workflow-config", help="Path to the workflow config file")
    parser.add_argument("--cron-interval", help="Cron interval for scheduling tasks (e.g. '*/5' for every 5 minutes)")
    parser.add_argument("--run-immediately", action="store_true", help="Run the task immediately when started")
    parser.add_argument("--reset-lock", action="store_true", help="Run the task while bypassing the process lock, if set.")
    args = parser.parse_args()
    return args

def get_cron_interval():
    """
    Get the cron interval from command line argument, environment variable, or default value.
    Command line argument takes precedence over environment variable.
    """

    # The function get_cron_interval() is executed before argparse is processed in the main() function;
    # hence, the following code is used to ensure proper argument (--cron-interval) parsing.
    args = args_parse_aimoa()

    default_interval = '*/5'
    env_interval = os.environ.get('CRON_INTERVAL')
    
    if args and args.cron_interval:
        if env_interval:
            logger.info(f"Overriding environment variable CRON_INTERVAL={env_interval} with command line argument: {args.cron_interval}")
        else:
            logger.info(f"Using cron interval from command line argument: {args.cron_interval}")
        return args.cron_interval
    elif env_interval:
        logger.info(f"Using cron interval from environment variable CRON_INTERVAL: {env_interval}")
        return env_interval
    else:
        logger.info(f"No cron interval specified. Using default value: {default_interval}")
        return default_interval

@huey.periodic_task(crontab(minute=get_cron_interval()))
def schedule_tasks() -> None:
    """
    Periodic task triggered to process workflows.
    """
    logger.info("Running scheduled tasks")
    try:
        process_workflow_task(config_file, workflow_config_file, reset_lock)
    except Exception as e:
        logger.exception("Error during scheduled task execution: %s", e)

    logger.info("Scheduled tasks completed")

def signal_handler(signum, frame):
    logger.info("Received signal %s. Initiating shutdown...", signum)
    shutdown_event.set()

def main_loop():
    try:
        logger.info("Main loop started. Waiting for tasks...")
        while not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Initiating shutdown...")
    finally:
        shutdown_event.set()
        logger.info("Main loop ended.")

if __name__ == "__main__":
    args = args_parse_aimoa()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration files
    config_file = args.config or os.environ.get('AIMOA_CONFIG') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
    workflow_config_file = args.workflow_config or os.environ.get('AIMOA_WORKFLOW_CONFIG') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflow-config.yaml")
    reset_lock = args.reset_lock    
    
    try:
        check_config_files_exist(config_file, workflow_config_file)
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Check for run_immediately option
    run_immediately = args.run_immediately or os.environ.get('RUN_IMMEDIATELY', '').lower() in ('true', '1', 'yes')

    consumer = Consumer(huey)
    main_thread = threading.Thread(target=main_loop)
    main_thread.start()

    if run_immediately:
        logger.info("Running task immediately...")
        process_workflow_task(config_file, workflow_config_file, reset_lock)

    try:
        logger.info("Starting Huey consumer...")
        consumer.run()
    except Exception as e:
        logger.exception("Error in consumer: %s", e)
    finally:
        logger.info("Stopping consumer...")
        consumer.stop()
        shutdown_event.set()
        main_thread.join()
        logger.info("Main thread joined. Exiting...")
