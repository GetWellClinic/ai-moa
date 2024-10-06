"""
Module for loading and saving configuration files.

This module provides functions to load configuration from a YAML file
and save configuration back to a YAML file.

Dependencies:
- yaml: For parsing and dumping YAML files
- os: For file path operations
"""

import yaml
import os

def load_config(filename=None):
    """
    Load configuration from a YAML file.

    If no filename is provided, it defaults to 'config.yaml' in the same
    directory as this script.

    Args:
        filename (str, optional): Path to the configuration file.

    Returns:
        dict: Loaded configuration as a dictionary.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def save_config(config, filename=None):
    """
    Save configuration to a YAML file.

    If no filename is provided, it defaults to 'config.yaml' in the same
    directory as this script.

    Args:
        config (dict): Configuration to save.
        filename (str, optional): Path to the configuration file.

    Raises:
        IOError: If there's an error writing to the file.
        yaml.YAMLError: If there's an error dumping the configuration to YAML.
    """
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
