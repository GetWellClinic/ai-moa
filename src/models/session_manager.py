import requests
import logging

class SessionManager:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def login(self):
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
        return self.session
