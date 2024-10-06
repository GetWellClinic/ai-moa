"""
Module for handling login operations in the Oscar EMR system.

This module contains the Login class which manages the authentication
process for the Oscar EMR system using Selenium WebDriver.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from utils.config_manager import ConfigManager

class Login:
    """
    Class for handling login operations in the Oscar EMR system.

    This class provides methods for authenticating users in the Oscar EMR system
    using Selenium WebDriver.

    Attributes:
        config (ConfigManager): Configuration manager containing login credentials and URLs.
        session_manager: SessionManager object for handling EMR sessions.
    """

    def __init__(self, config: ConfigManager, session_manager):
        """
        Initialize Login with configuration and session manager.

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
        and submits the login form.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL of the login page.

        Returns:
            str: The current URL after login attempt.
        """
        driver.get(login_url)
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        pin_field = driver.find_element(By.NAME, "pin")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        pin_field.send_keys(self.pin)
        pin_field.send_keys(Keys.RETURN)

        return driver.current_url
