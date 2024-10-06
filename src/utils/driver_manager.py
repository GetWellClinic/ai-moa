"""
Module for managing WebDriver instances in the Oscar EMR system.

This module contains the DriverManager class which centralizes the creation
and configuration of WebDriver instances for use across the application.

Dependencies:
- selenium: For web automation
- webdriver_manager: For automatic management of WebDriver binaries
- utils.config_manager: For accessing configuration settings
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.config_manager import ConfigManager


class DriverManager:
    """
    Class for managing WebDriver instances in the Oscar EMR system.

    This class provides methods for creating and configuring WebDriver
    instances to be used across different parts of the application.

    Attributes:
        config (ConfigManager): Configuration manager containing system settings.
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize DriverManager with configuration.

        Args:
            config (ConfigManager): Configuration manager containing system settings.
        """
        self.config = config

    def get_driver(self):
        """
        Create and configure a Chrome WebDriver instance.

        This method sets up a Chrome WebDriver with options specified in the
        configuration. It uses the webdriver_manager to automatically manage
        the ChromeDriver binary.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance.
        """
        chrome_options = Options()
        if self.config.get('chrome_options', {}).get('headless', False):
            chrome_options.add_argument("--headless")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
