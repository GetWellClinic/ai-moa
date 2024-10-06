"""
Module for managing sessions in the Oscar EMR system.

This module contains the SessionManager class which handles session
creation and management for interactions with the Oscar EMR system.
"""

import requests
import logging


class SessionManager:
    """
    Class for managing sessions in the Oscar EMR system.

    This class provides methods for creating and maintaining a session
    with the Oscar EMR system, including login functionality.

    Attributes:
        config: Configuration object containing login credentials and URLs.
        session (requests.Session): Session object for making HTTP requests.
        logger (logging.Logger): Logger instance for this class.
    """

    def __init__(self, config):
        """
        Initialize SessionManager with configuration.

        Args:
            config: Configuration object containing login credentials and URLs.
        """
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def login(self):
        """
        Perform login and establish a session.

        This method sends a POST request to the login URL with the
        provided credentials to establish a session.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        login_url = f"{self.config.base_url}{self.config.get('urls', {}).get('login', '')}"
        response = self.session.post(
            login_url,
            data={
                "username": self.config.user_login['username'],
                "password": self.config.user_login['password'],
                "pin": self.config.user_login['pin']
            }
        )
        
        if response.url == login_url:
            self.logger.error("Login failed.")
            return False
        else:
            self.logger.info("Login successful!")
            return True

    def get_session(self):
        """
        Return the current session object.

        Returns:
            requests.Session: The current session object.
        """
        return self.session
