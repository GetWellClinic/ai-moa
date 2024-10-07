"""
Module for managing WebDriver instances for Selenium automation.

This module provides a DriverManager class that handles the creation and
configuration of WebDriver instances, specifically for Chrome browsers.
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from ..config import ConfigManager

logger = logging.getLogger(__name__)

class DriverManager:
    """
    A class for managing WebDriver instances.

    This class is responsible for creating and configuring WebDriver
    instances based on the provided configuration.

    Attributes:
        config (ConfigManager): An instance of ConfigManager containing
                                the configuration settings.
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize the DriverManager with a configuration.

        Args:
            config (ConfigManager): An instance of ConfigManager containing
                                    the configuration settings.
        """
        self.config = config
        logger.debug("DriverManager initialized")

    def get_driver(self):
        """
        Create and return a configured WebDriver instance.

        This method creates a Chrome WebDriver instance with options
        set according to the configuration.

        Returns:
            webdriver.Chrome: A configured Chrome WebDriver instance.
        """
        logger.info("Creating new WebDriver instance")
        chrome_options = Options()
        if self.config.get('chrome.options.headless', False):
            chrome_options.add_argument("--headless")
            logger.debug("Chrome headless mode enabled")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
