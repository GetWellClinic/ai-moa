"""
Module Name: login_manager.py

Description:
    This module handles login operations for the EMR system.
    It provides the LoginManager class to authenticate users using either Selenium or requests sessions.

Author:
    Spring Health Corporation

License:
    Refer to the LICENSE file for detailed licensing information.
"""

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests

from config import ConfigManager

logger = logging.getLogger(__name__)

class LoginManager:
    """
    Handles login operations for the EMR system.

    This class provides methods to authenticate users using either Selenium or requests sessions.

    :param config: Configuration manager with login credentials and URLs.
    :type config: ConfigManager
    :ivar username: The username for EMR login.
    :vartype username: str
    :ivar password: The password for EMR login.
    :vartype password: str
    :ivar pin: The PIN for EMR login.
    :vartype pin: str
    :ivar base_url: The base URL of the EMR system.
    :vartype base_url: str
    :ivar login_url: The full login URL constructed from the base URL.
    :vartype login_url: str
    """

    def __init__(self, config: ConfigManager):
        """
        Initializes the LoginManager with user credentials and URLs.

        :param config: Configuration manager with login credentials and URLs.
        :type config: ConfigManager
        """
        self.config = config
        self.username = config.get('user_login', {}).get('username')
        self.password = config.get('user_login', {}).get('password')
        self.pin = config.get('user_login', {}).get('pin')
        self.base_url = config.get('base_url')
        self.login_url = f"{self.base_url}/login.do"
        logger.debug("LoginManager initialized")

    def login_with_selenium(self, driver):
        """
        Perform login using Selenium WebDriver.

        Navigates to the login page and submits the login form.

        :param driver: Selenium WebDriver instance.
        :type driver: selenium.webdriver.Chrome
        :return: The current URL after login attempt.
        :rtype: str
        """
        logger.info(f"Attempting Selenium login for user: {self.username}")
        driver.get(self.login_url)

        # Locate the login fields and enter credentials
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        pin_field = driver.find_element(By.NAME, "pin")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        pin_field.send_keys(self.pin)

        # Submit the login form
        pin_field.send_keys(Keys.RETURN)
        logger.debug("Login form submitted")

        return driver.current_url

    def login_with_requests(self):
        """
        Perform login using a requests session.

        Sends a POST request to the login URL with credentials.

        :return: A tuple containing the session and a boolean indicating success.
        :rtype: Tuple[requests.Session, bool]
        """
        logger.info(f"Attempting requests login for user: {self.username}")
        session = requests.Session()
        response = session.post(
            self.login_url,
            data={
                "username": self.username,
                "password": self.password,
                "pin": self.pin
            }
        )

        login_successful = response.url != self.login_url
        logger.debug(f"Login {'successful' if login_successful else 'failed'}")
        return session, login_successful

    def is_login_successful(self, current_url):
        """
        Check if the login was successful based on the current URL.

        :param current_url: The URL after attempting to log in.
        :type current_url: str
        :return: True if login was successful, False otherwise.
        :rtype: bool
        """
        logger.debug(f"Checking login success. Current URL: {current_url}")
        return current_url != self.login_url
