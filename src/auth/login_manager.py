import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests

from config import ConfigManager

logger = logging.getLogger(__name__)

class LoginManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.username = config.get('user_login', {}).get('username')
        self.password = config.get('user_login', {}).get('password')
        self.pin = config.get('user_login', {}).get('pin')
        self.base_url = config.get('base_url')
        self.login_url = f"{self.base_url}/login.do"
        logger.debug("LoginManager initialized")

    def login_with_selenium(self, driver):
        logger.info(f"Attempting Selenium login for user: {self.username}")
        driver.get(self.login_url)

        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        pin_field = driver.find_element(By.NAME, "pin")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        pin_field.send_keys(self.pin)

        pin_field.send_keys(Keys.RETURN)
        logger.debug("Login form submitted")

        return driver.current_url

    def login_with_requests(self):
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
        logger.debug(f"Checking login success. Current URL: {current_url}")
        return current_url != self.login_url
