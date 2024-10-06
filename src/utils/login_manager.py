"""
Module for managing login operations in the Oscar EMR system.

This module contains the LoginManager class which centralizes the authentication
process for the Oscar EMR system using Selenium WebDriver and requests.

The module provides functionality to:
1. Initialize login credentials from configuration
2. Perform login operations using Selenium WebDriver
3. Perform login operations using requests for session management
4. Handle login callbacks and URL verification

Dependencies:
- selenium: For web automation
- requests: For session management
- utils.config_manager: For accessing configuration settings
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests

from utils.config_manager import ConfigManager


class LoginManager:
    """
    Class for managing login operations in the Oscar EMR system.

    This class provides methods for authenticating users in the Oscar EMR system
    using both Selenium WebDriver and requests. It manages login credentials and
    performs the login process.

    Attributes:
        config (ConfigManager): Configuration manager containing login
                                credentials and URLs.
        username (str): Username for login.
        password (str): Password for login.
        pin (str): PIN for login.
        base_url (str): Base URL of the EMR system.
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize LoginManager with configuration.

        This method sets up the login credentials and base URL from the provided
        configuration.

        Args:
            config (ConfigManager): Configuration manager containing login
                                    credentials and URLs.
        """
        self.config = config
        self.username = config.get('user_login', {}).get('username')
        self.password = config.get('user_login', {}).get('password')
        self.pin = config.get('user_login', {}).get('pin')
        self.base_url = config.get('base_url')

    def login_with_selenium(self, driver):
        """
        Perform the login operation using Selenium WebDriver.

        This method navigates to the login page, enters the credentials,
        and submits the login form. It uses Selenium's WebDriver to interact
        with the web elements.

        Args:
            driver: Selenium WebDriver instance.

        Returns:
            str: The current URL after login attempt.
        """
        login_url = f"{self.base_url}/login.do"
        driver.get(login_url)

        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        pin_field = driver.find_element(By.NAME, "pin")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        pin_field.send_keys(self.pin)

        pin_field.send_keys(Keys.RETURN)

        return driver.current_url

    def login_with_requests(self):
        """
        Perform login and establish a session using requests.

        This method sends a POST request to the login URL with the
        provided credentials to establish a session. It checks the response
        URL to determine if the login was successful.

        Returns:
            tuple: (requests.Session, bool) - The session object and a boolean
                   indicating whether the login was successful.
        """
        session = requests.Session()
        response = session.post(
            f"{self.base_url}/login.do",
            data={
                "username": self.username,
                "password": self.password,
                "pin": self.pin
            }
        )

        login_successful = response.url != f"{self.base_url}/login.do"
        return session, login_successful

    def is_login_successful(self, current_url):
        """
        Check if the login was successful based on the current URL.

        Args:
            current_url (str): The current URL after login attempt.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        return current_url != f"{self.base_url}/login.do"
