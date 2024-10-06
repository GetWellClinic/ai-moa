"""
Module for managing configuration settings.

This module contains the ConfigManager class which handles loading,
saving, and accessing configuration settings for the application.

The module provides functionality to:
1. Load configuration from a YAML file
2. Access configuration settings
3. Manage workflow-specific configurations

Dependencies:
- yaml: For parsing YAML files
- typing: For type hinting
"""

from typing import Dict, Any, List

import yaml


class ConfigManager:
    """
    Class for managing configuration settings.

    This class provides methods for loading and accessing
    configuration settings stored in a YAML file.

    Attributes:
        config_path (str): Path to the configuration file.
        config (Dict[str, Any]): Dictionary containing the configuration
                                 settings.
    """

    def __init__(self, config_path: str):
        """
        Initialize ConfigManager with the path to the configuration file.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the YAML file.

        Returns:
            Dict[str, Any]: Dictionary containing the configuration settings.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            yaml.YAMLError: If there's an error parsing the YAML file.
        """
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key (str): The configuration key to retrieve.
            default (Any, optional): Default value if the key is not found.

        Returns:
            Any: The value associated with the key, or the default value if not
                 found.
        """
        return self.config.get(key, default)

    @property
    def workflow_steps(self) -> List[Dict[str, Any]]:
        """
        Get the workflow steps.

        Returns:
            List[Dict[str, Any]]: List of workflow steps with their decision
                                  paths.
        """
        return self.config['workflow']['steps']

    def get_next_step(self, current_step: str, outcome: bool) -> str:
        """
        Get the next step based on the current step and its outcome.

        Args:
            current_step (str): The name of the current step.
            outcome (bool): The outcome of the current step (True or False).

        Returns:
            str: The name of the next step, or None if not found.
        """
        for step in self.workflow_steps:
            if step['name'] == current_step:
                return step['true_next'] if outcome else step['false_next']
        return None

    @property
    def document_categories(self) -> List[str]:
        """
        Get the document categories.

        Returns:
            List[str]: List of document categories.
        """
        return self.config['document_categories']

    @property
    def ai_prompts(self) -> Dict[str, str]:
        """
        Get the AI prompts.

        Returns:
            Dict[str, str]: Dictionary of AI prompts.
        """
        return self.config['ai_prompts']
