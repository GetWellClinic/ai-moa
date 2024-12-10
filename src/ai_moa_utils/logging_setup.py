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
from logging.handlers import RotatingFileHandler
from config.config_manager import ConfigManager

import os

def setup_logging(config: ConfigManager):
    """
    Set up logging for the application, including both file and console handlers.
    
    This function configures a root logger to output logs to both the console 
    and a rotating log file. The log level and format are determined by the 
    provided configuration.

    If both the `RotatingFileHandler` and `StreamHandler` are already set 
    for the root logger, the function will not modify the existing logging 
    configuration and will simply return the existing logger.

    Args:
        config (ConfigManager): A configuration manager instance that provides
                                the logging configuration.

    Returns:
        logging.Logger: The configured root logger with the appropriate handlers.
    
    Configuration options:
        - 'logging.format': A string defining the log message format. Defaults to 
          '%(asctime)s - %(name)s - %(levelname)s - %(message)s'.
        - 'logging.filename': The log file name. Defaults to 'workflow.log'.
        - 'logging.file_level': The log level for file handler. Defaults to 'DEBUG'.
        - 'logging.console_level': The log level for console handler. Defaults to 'INFO'.

    Example:
        config = ConfigManager()
        logger = setup_logging(config)
        logger.debug("This is a debug message.")
    """
    logging_config = config.get('logging', {})
    
    # Set up root logger
    root_logger = logging.getLogger()

    # Check if the specific handlers already exist
    file_handler_exists = any(isinstance(handler, RotatingFileHandler) for handler in root_logger.handlers)
    console_handler_exists = any(isinstance(handler, logging.StreamHandler) for handler in root_logger.handlers)

    # If both handlers exist, return the logger without modifying it
    if file_handler_exists and console_handler_exists:
        return root_logger

    # Set root logger level to the more permissive of file and console levels
    file_level = logging.getLevelName(logging_config.get('file_level', 'DEBUG'))
    console_level = logging.getLevelName(logging_config.get('console_level', 'INFO'))
    root_logger.setLevel(min(file_level, console_level))

    # Create formatters
    formatter = logging.Formatter(logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # File Handler
    log_file = logging_config.get('filename', 'workflow.log')
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger
