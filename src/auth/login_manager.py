from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests

from config import ConfigManager


class LoginManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.username = config.get('user_login', {}).get('username')
        self.password = config.get('user_login', {}).get('password')
        self.pin = config.get('user_login', {}).get('pin')
        self.base_url = config.get('base_url')
        self.login_url = f"{self.base_url}/login.do"

    def login_with_selenium(self, driver):
        driver.get(self.login_url)

        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        pin_field = driver.find_element(By.NAME, "pin")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        pin_field.send_keys(self.pin)

        pin_field.send_keys(Keys.RETURN)

        return driver.current_url

    def login_with_requests(self):
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
        return session, login_successful

    def is_login_successful(self, current_url):
        return current_url != self.login_url
