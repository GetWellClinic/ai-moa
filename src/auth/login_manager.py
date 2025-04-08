# COPYRIGHT © 2024 by Spring Health Corporation <office(at)springhealth.org>
# Toronto, Ontario, Canada
# SUMMARY: This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software,
# documentation, and configuration files.
# These programs, documentation, and configuration files are made available to you as open source
# in the hopes that your clinic or organization may find it useful and improve your care to the public
# by reducing administrative burden for your staff and service providers.
# NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
# and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
# LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
# Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.
# ***
# NOTICE: We hope that you will consider contributing to our common source code repository so that
# others may benefit from your shared work.
# However, if you distribute this code or serve this application to users in modified form,
# or as part of a derivative work, you are required to make your modified or derivative work
# source code available under the same herein described license.
# Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work
# source code can be acquired publicly in its latest most up-to-date version, within one month.
# ***

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import ConfigManager

logger = logging.getLogger(__name__)

class LoginManager:
    """
    Handles login operations for the EMR system.

    This class provides methods to authenticate users using either Selenium or requests sessions.

    :param config: Configuration manager with login credentials and URLs.
    :type config: ConfigManager
    :ivar username: The username for EMR login.
    :vartype username: str
    :ivar password: The password for EMR login.
    :vartype password: str
    :ivar pin: The PIN for EMR login.
    :vartype pin: str
    :ivar base_url: The base URL of the EMR system.
    :vartype base_url: str
    :ivar login_url: The full login URL constructed from the base URL.
    :vartype login_url: str
    """

    def __init__(self, config: ConfigManager):
        """
        Initializes the LoginManager with user credentials and URLs.

        :param config: Configuration manager with login credentials and URLs.
        :type config: ConfigManager
        """
        self.config = config
        self.username = config.get('emr.username')
        self.password = config.get('emr.password')
        self.pin = config.get('emr.pin')
        self.base_url = config.get('emr.base_url')
        self.login_url = ""
        logger.debug("LoginManager initialized")

    def login_with_selenium(self, driver):
        """
        Perform login using Selenium WebDriver.

        Navigates to the login page and submits the login form.

        :param driver: Selenium WebDriver instance.
        :type driver: selenium.webdriver.Chrome
        :return: The current URL after login attempt.
        :rtype: str
        """
        logger.info(f"Attempting Selenium login for user.")

        # Print is used to avoid logging username into log file.
        print(f"Attempting Selenium login for user: {self.username}")
        
        need_pin_field = self.config.get('emr.login_pin_field', False)
        system_type = self.config.get('emr.system_type', 'o19')
        
        driver.get(self.base_url)
        
        driver.implicitly_wait(30)

        # Locate the login fields and enter credentials
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        self.login_url = driver.current_url

        if(need_pin_field):
            if(system_type == 'o19'):
                pin_field = driver.find_element(By.NAME, "pin2")
            else:
                pin_field = driver.find_element(By.NAME, "pin")
            pin_field.send_keys(self.pin)

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        if(need_pin_field):
            # Submit the login form
            pin_field.send_keys(Keys.RETURN)
        else:
            password_field.send_keys(Keys.RETURN)

        logger.debug("Login form submitted")

        try:
            firstmenu_field = driver.find_element(By.ID, "firstMenu")
            return driver.current_url
        except TimeoutException:
            logger.debug("Timeout, element not found")
            return self.login_url
        except NoSuchElementException:
            logger.debug("Error; element not found")
            return self.login_url


    def get_driver(self):
        """
        Retrieves a Selenium WebDriver instance for interaction with the web-based system.

        This method configures Chrome options and creates a Chrome WebDriver instance using 
        the `webdriver_manager` library. It then attempts to log in using Selenium. If login is successful, 
        the driver instance is returned, otherwise, it returns `False`.

        Returns:
            webdriver.Chrome | bool: The WebDriver instance if login is successful, 
            `False` otherwise.

        Example:
            >>> driver = manager.get_driver()
            >>> print(driver)
            <selenium.webdriver.chrome.webdriver.WebDriver object at 0x...>  # if login is successful
        """
        chrome_options = Options()
        if self.config.get('chrome.options.headless', False):
                chrome_options.add_argument("--headless")
                logger.debug("Chrome headless mode enabled")
        if not self.config.get('emr.verify-HTTPS', False):
            chrome_options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver, self.is_login_successful(self.login_with_selenium(driver))

    def login(self):
        """
        Perform login using a requests session with exponential backoff retry.

        Sends a POST request to the login URL with credentials.

        :return: A tuple containing the session and a boolean indicating success.
        :rtype: Tuple[requests.Session, bool]
        """
        logger.info("Creating session and driver.")
        session = requests.Session()
        
        driver, flag = self.get_driver()

        if flag:
            session = self.get_driver_session(session, driver)
            return session, driver, flag
        else:
            return session, driver, flag

    def is_login_successful(self, current_url):
        """
        Check if the login was successful based on the current URL.

        :param current_url: The URL after attempting to log in.
        :type current_url: str
        :return: True if login was successful, False otherwise.
        :rtype: bool
        """
        logger.debug(f"Checking login success. Current URL: {current_url}")
        return current_url != self.login_url

    def get_driver_session(self, session, driver):
        """
        Retrieves the session cookies from a Selenium WebDriver and sets them in the current session.

        Args:
        driver (selenium.webdriver): The Selenium WebDriver instance from which cookies will
                                      be retrieved.

        Returns:
            Session: This method returns session cookies from selenium webdriver.
        """
        cookies = driver.get_cookies()
        
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        return session
