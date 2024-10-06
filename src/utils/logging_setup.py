"""
Module for setting up logging configuration.

This module provides a function to set up logging based on the
provided configuration settings.

The module offers functionality to:
1. Configure the root logger with specified settings
2. Set up logging format and level

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
                               'root': {
                                   'level': 'INFO'  # or DEBUG, WARNING, ERROR, CRITICAL
                               }
                           }
                       }

    Returns:
        None

    Note:
        If the logging configuration is not found in the config dictionary,
        it defaults to INFO level logging.
    """
    logging.basicConfig(
        level=config.get('logging', {}).get('root', {}).get('level', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Optionally, you can add more sophisticated logging setup here
    # For example, setting up file handlers, configuring loggers for different modules, etc.
