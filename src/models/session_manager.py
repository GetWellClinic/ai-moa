import requests
import logging


class SessionManager:
    """Class for managing sessions in the Oscar EMR system."""

    def __init__(self, config):
        """Initialize SessionManager with configuration."""
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def login(self):
        """Perform login and establish a session."""
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
        """Return the current session object."""
        return self.session
