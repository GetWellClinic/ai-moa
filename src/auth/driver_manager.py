from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.config_manager import ConfigManager


class DriverManager:
    def __init__(self, config: ConfigManager):
        self.config = config

    def get_driver(self):
        chrome_options = Options()
        if self.config.get('chrome_options', {}).get('headless', False):
            chrome_options.add_argument("--headless")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
