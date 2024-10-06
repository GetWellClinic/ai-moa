from utils.config_manager import ConfigManager
from .login_manager import LoginManager


class SessionManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.login_manager = LoginManager(config)
        self.session, login_successful = self.login_manager.login_with_requests()
        if login_successful:
            print("Login successful!")
        else:
            print("Login failed.")

    def login(self):
        self.session, login_successful = self.login_manager.login_with_requests()
        return login_successful

    def get_session(self):
        return self.session
