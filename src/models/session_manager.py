"""
Module for managing sessions in the Oscar EMR system.

This module contains the SessionManager class which handles session
creation and management for interactions with the Oscar EMR system.

The module provides functionality to:
1. Initialize a session with login credentials
2. Perform login to establish a session
3. Maintain and retrieve the current session

Dependencies:
- requests: For making HTTP requests
- utils.config_manager: For accessing configuration settings
"""

import requests

from utils.config_manager import ConfigManager

class SessionManager:
    """
    Class for managing sessions in the Oscar EMR system.

    This class provides methods for creating and maintaining a session
    with the Oscar EMR system, including login functionality.

    Attributes:
        config (ConfigManager): Configuration manager containing login credentials and URLs.
        session (requests.Session): Session object for making HTTP requests.
        username (str): Username for login.
        password (str): Password for login.
        pin (str): PIN for login.
        base_url (str): Base URL of the EMR system.
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize SessionManager with configuration.

        This method sets up the session and login credentials from the provided
        configuration. It also attempts to log in immediately upon initialization.

        Args:
            config (ConfigManager): Configuration manager containing login credentials and URLs.
        """
        self.config = config
        self.session = requests.Session()
        self.username = config.get('user_login', {}).get('username')
        self.password = config.get('user_login', {}).get('password')
        self.pin = config.get('user_login', {}).get('pin')
        self.base_url = config.get('base_url')
        self.login()

    def login(self):
        """
        Perform login and establish a session.

        This method sends a POST request to the login URL with the
        provided credentials to establish a session. It checks the response
        URL to determine if the login was successful.

        Returns:
            bool: True if login was successful, False otherwise.

        Note:
            This method prints the login status to the console. In a production
            environment, consider using proper logging instead of print statements.
        """
        response = self.session.post(
            f"{self.base_url}/login.do",
            data={
                "username": self.username,
                "password": self.password,
                "pin": self.pin
            }
        )
        
        if response.url == f"{self.base_url}/login.do":
            print("Login failed.")
            return False
        else:
            print("Login successful!")
            return True

    def get_session(self):
        """
        Return the current session object.

        This method provides access to the current requests.Session object,
        which can be used to make authenticated requests to the EMR system.

        Returns:
            requests.Session: The current session object.
        """
        return self.session
