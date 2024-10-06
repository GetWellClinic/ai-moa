"""
Module for managing sessions in the Oscar EMR system.

This module provides a SessionManager class that handles the creation
and management of sessions, including login functionality.
"""

import logging
from config import ConfigManager
from .login_manager import LoginManager

logger = logging.getLogger(__name__)

class SessionManager:
    """
    A class for managing sessions in the Oscar EMR system.

    This class is responsible for creating and maintaining sessions,
    including handling the login process.

    Attributes:
        config (ConfigManager): An instance of ConfigManager containing
                                the configuration settings.
        login_manager (LoginManager): An instance of LoginManager for
                                      handling login operations.
        session: The current session object.
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize the SessionManager with a configuration.

        This constructor creates a LoginManager instance and attempts
        to log in immediately upon creation.

        Args:
            config (ConfigManager): An instance of ConfigManager containing
                                    the configuration settings.
        """
        self.config = config
        self.login_manager = LoginManager(config)
        self.session, login_successful = self.login_manager.login_with_requests()
        if login_successful:
            logger.info("Login successful!")
        else:
            logger.error("Login failed.")
        logger.debug("SessionManager initialized")

    def login(self):
        """
        Attempt to log in and create a new session.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        logger.info("Attempting to log in and create a new session")
        self.session, login_successful = self.login_manager.login_with_requests()
        return login_successful

    def get_session(self):
        """
        Get the current session object.

        Returns:
            The current session object.
        """
        logger.debug("Retrieving current session")
        return self.session
