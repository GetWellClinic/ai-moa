import os
import yaml
from typing import Dict, Any


class ConfigManager:
    """Class for managing configuration settings."""

    def __init__(self, config_path: str):
        """Initialize ConfigManager with the path to the configuration file."""
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from the YAML file."""
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)

    def save_config(self):
        """Save the current configuration to the YAML file."""
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value and save it."""
        self.config[key] = value
        self.save_config()

    @property
    def user_login(self) -> Dict[str, str]:
        """Get user login information."""
        return self.config['user_login']

    @property
    def base_url(self) -> str:
        """Get the base URL for the Oscar EMR system."""
        return self.config['base_url']

    @property
    def last_processed_pdf(self) -> str:
        """Get the timestamp of the last processed PDF."""
        return self.config['last_processed_pdf']

    @last_processed_pdf.setter
    def last_processed_pdf(self, value: str):
        """Set the timestamp of the last processed PDF."""
        self.config['last_processed_pdf'] = value
        self.save_config()

    @property
    def last_pending_doc_file(self) -> str:
        """Get the last pending document file."""
        return self.config['last_pending_doc_file']

    @last_pending_doc_file.setter
    def last_pending_doc_file(self, value: str):
        """Set the last pending document file."""
        self.config['last_pending_doc_file'] = value
        self.save_config()

    @property
    def enable_ocr_gpu(self) -> bool:
        """Check if GPU-enabled OCR is enabled."""
        return self.config['enable_ocr_gpu']

    @property
    def workflow_file_path(self) -> str:
        """Get the path to the workflow file."""
        return self.config.get('workflow_file_path', 'workflow.csv')

    @property
    def chrome_options(self) -> Dict[str, Any]:
        """Get Chrome browser options."""
        return self.config['chrome_options']

    @property
    def ai_config(self) -> Dict[str, Any]:
        """Get AI configuration settings."""
        return self.config.get('ai_config', {})
