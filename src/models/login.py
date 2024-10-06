"""
Module for handling login operations in the Oscar EMR system.

This module contains the Login class which serves as a wrapper for the
LoginManager, providing backward compatibility for existing code.

Dependencies:
- utils.config_manager: For accessing configuration settings
- utils.login_manager: For centralized login logic
"""

from utils.config_manager import ConfigManager
from utils.login_manager import LoginManager


class Login:
    """
    Class for handling login operations in the Oscar EMR system.

    This class serves as a wrapper for the LoginManager, providing
    backward compatibility for existing code.

    Attributes:
        login_manager (LoginManager): Instance of LoginManager for handling
                                      login operations.
    """

    def __init__(self, config: ConfigManager, session_manager):
        """
        Initialize Login with configuration and session manager.

        This method creates an instance of LoginManager using the provided
        configuration.

        Args:
            config (ConfigManager): Configuration manager containing login
                                    credentials and URLs.
            session_manager: SessionManager object for handling EMR sessions.
                             (kept for backward compatibility)
        """
        self.login_manager = LoginManager(config)

    def login_successful_callback(self, driver):
        """
        Callback method to be used after a login attempt.

        This method is kept for backward compatibility and uses the
        LoginManager to perform the login operation.

        Args:
            driver: Selenium WebDriver instance.

        Returns:
            str: The current URL after login attempt.
        """
        return self.login_manager.login_with_selenium(driver)

    def login(self, driver, login_url):
        """
        Perform the login operation using Selenium WebDriver.

        This method is kept for backward compatibility and uses the
        LoginManager to perform the login operation.

        Args:
            driver: Selenium WebDriver instance.
            login_url (str): URL of the login page. (not used)

        Returns:
            str: The current URL after login attempt.
        """
        return self.login_manager.login_with_selenium(driver)
