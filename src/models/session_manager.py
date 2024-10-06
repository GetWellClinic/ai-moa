"""
Module for managing sessions in the Oscar EMR system.

This module contains the SessionManager class which handles session
creation and management for interactions with the Oscar EMR system.

The module provides functionality to:
1. Initialize a session with login credentials
2. Perform login to establish a session
3. Maintain and retrieve the current session

Dependencies:
- utils.config_manager: For accessing configuration settings
- utils.login_manager: For centralized login logic
"""

from utils.config_manager import ConfigManager
from utils.login_manager import LoginManager


class SessionManager:
    """
    Class for managing sessions in the Oscar EMR system.

    This class provides methods for creating and maintaining a session
    with the Oscar EMR system, including login functionality.

    Attributes:
        config (ConfigManager): Configuration manager containing login
                                credentials and URLs.
        login_manager (LoginManager): Instance of LoginManager for handling
                                      login operations.
        session: Session object for making HTTP requests.
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize SessionManager with configuration.

        This method sets up the login manager and attempts to log in
        immediately upon initialization.

        Args:
            config (ConfigManager): Configuration manager containing login
                                    credentials and URLs.
        """
        self.config = config
        self.login_manager = LoginManager(config)
        self.session, login_successful = self.login_manager.login_with_requests()
        if login_successful:
            print("Login successful!")
        else:
            print("Login failed.")

    def login(self):
        """
        Perform login and establish a session.

        This method uses the LoginManager to perform the login operation
        and establish a session.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        self.session, login_successful = self.login_manager.login_with_requests()
        return login_successful

    def get_session(self):
        """
        Return the current session object.

        This method provides access to the current session object,
        which can be used to make authenticated requests to the EMR system.

        Returns:
            The current session object.
        """
        return self.session
