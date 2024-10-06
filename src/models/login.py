"""
Module for handling login operations in the Oscar EMR system.

This module contains the Login class which manages the authentication
process for the Oscar EMR system using Selenium WebDriver.

The module provides functionality to:
1. Initialize login credentials from configuration
2. Perform login operations using Selenium WebDriver
3. Handle login callbacks and URL verification

Dependencies:
- selenium: For web automation
- utils.config_manager: For accessing configuration settings
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from utils.config_manager import ConfigManager

class Login:
    """
    Class for handling login operations in the Oscar EMR system.

    This class provides methods for authenticating users in the Oscar EMR system
    using Selenium WebDriver. It manages login credentials and performs the login
    process.

    Attributes:
        config (ConfigManager): Configuration manager containing login credentials and URLs.
        session_manager: SessionManager object for handling EMR sessions.
        username (str): Username for login.
        password (str): Password for login.
        pin (str): PIN for login.
        base_url (str): Base URL of the EMR system.
    """

    def __init__(self, config: ConfigManager, session_manager):
        """
        Initialize Login with configuration and session manager.

        This method sets up the login credentials and base URL from the provided
        configuration. It also stores a reference to the session manager.

        Args:
            config (ConfigManager): Configuration manager containing login credentials and URLs.
            session_manager: SessionManager object for handling EMR sessions.
        """
        self.config = config
        self.session_manager = session_manager
        self.username = config.get('user_login', {}).get('username')
        self.password = config.get('user_login', {}).get('password')
        self.pin = config.get('user_login', {}).get('pin')
        self.base_url = config.get('base_url')

    def login_successful_callback(self, driver):
        """
        Callback method to be used after a successful login attempt.

        This method is typically called after a login attempt to verify success
        and perform any necessary post-login actions.

        Args:
            driver: Selenium WebDriver instance.

        Returns:
            str: The current URL after login attempt.
        """
        login_url = f"{self.base_url}/login.do"
        return self.login(driver, login_url)

    def login(self, driver, login_url):
        """
        Perform the login operation using Selenium WebDriver.

        This method navigates to the login page, enters the credentials,
        and submits the login form. It uses Selenium's WebDriver to interact
        with the web elements.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL of the login page.

        Returns:
            str: The current URL after login attempt.

        Note:
            This method assumes that the login page has input fields with names
            "username", "password", and "pin".
        """
        # Navigate to the login page
        driver.get(login_url)

        # Find and fill in the login form elements
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        pin_field = driver.find_element(By.NAME, "pin")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        pin_field.send_keys(self.pin)

        # Submit the form
        pin_field.send_keys(Keys.RETURN)

        # Return the current URL after login attempt
        return driver.current_url
