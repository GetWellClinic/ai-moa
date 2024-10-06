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
- logging: For logging configuration and usage
"""

from typing import Dict, Any, List
import yaml
import logging


class ConfigManager:
    """
    Class for managing configuration settings.

    This class provides methods for loading and accessing
    configuration settings stored in a YAML file.

    Attributes:
        config_path (str): Path to the configuration file.
        config (Dict[str, Any]): Dictionary containing the configuration
                                 settings.
        logger (logging.Logger): Logger instance for this class.
    """

    def __init__(self, config_path: str):
        """
        Initialize ConfigManager with the path to the configuration file.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logging()

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

    def setup_logging(self) -> logging.Logger:
        """
        Set up logging based on the configuration.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logging_config = self.config.get('logging', {})
        logging.basicConfig(
            level=logging_config.get('level', 'INFO'),
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            filename=logging_config.get('filename')
        )
        return logging.getLogger(__name__)

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

    def get_tasks_for_category(self, category_index: int) -> List[Dict[str, Any]]:
        """
        Get the tasks for a specific document category.

        Args:
            category_index (int): Index of the document category.

        Returns:
            List[Dict[str, Any]]: List of tasks for the specified category.
        """
        category_tasks = self.config.get('category_tasks', {})
        return category_tasks.get(str(category_index), [])

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
