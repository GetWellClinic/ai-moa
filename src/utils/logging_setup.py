"""
Module for setting up logging configuration.

This module provides functions to set up logging based on the
provided configuration settings.

The module offers functionality to:
1. Configure the root logger with specified settings
2. Set up logging format and level
3. Create and configure a logger instance

Dependencies:
- logging: Python's built-in logging module
"""

import logging

def setup_logging(config):
    """
    Set up logging configuration based on the provided config.

    This function configures the logging system using the settings
    provided in the config dictionary. It sets up the root logger
    with the specified log level and format.

    Args:
        config (dict): Configuration dictionary containing logging settings.
                       Expected structure:
                       {
                           'logging': {
                               'level': 'INFO',  # or DEBUG, WARNING, ERROR, CRITICAL
                               'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                               'filename': 'app.log'  # optional
                           }
                       }

    Returns:
        logging.Logger: Configured root logger instance
    """
    logging_config = config.get('logging', {})
    
    logging.basicConfig(
        level=logging_config.get('level', 'INFO'),
        format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        filename=logging_config.get('filename')
    )

    return logging.getLogger()

def get_logger(name, config):
    """
    Create and configure a logger instance.

    This function creates a new logger instance with the given name
    and configures it based on the provided config.

    Args:
        name (str): Name of the logger
        config (dict): Configuration dictionary containing logging settings

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(config.get('logging', {}).get('level', 'INFO'))
    return logger
