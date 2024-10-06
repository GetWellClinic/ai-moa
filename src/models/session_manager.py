"""
Module for managing sessions in the Oscar EMR system.

This module contains the SessionManager class which handles session
creation and management for interactions with the Oscar EMR system.
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
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize SessionManager with configuration.

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
        provided credentials to establish a session.

        Returns:
            bool: True if login was successful, False otherwise.
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

        Returns:
            requests.Session: The current session object.
        """
        return self.session
