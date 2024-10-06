"""
Module for setting up logging configuration.

This module provides a function to set up logging based on the
provided configuration settings.
"""

import logging


def setup_logging(config):
    """
    Set up logging configuration based on the provided config.

    This function configures the logging system using the settings
    provided in the config dictionary.

    Args:
        config (dict): Configuration dictionary containing logging settings.

    Returns:
        None
    """
    logging.basicConfig(
        level=config.get('logging', {}).get('root', {}).get('level', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
