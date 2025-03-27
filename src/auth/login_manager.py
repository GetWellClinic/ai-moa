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
        self.login_url = f"{self.base_url}/login.do"
        self.login_url_pro = f"{self.base_url}/#/"
        self.max_retries = config.get('login.max_retries', 5)
        self.initial_retry_delay = config.get('login.initial_retry_delay', 1)
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
        logger.info(f"Attempting Selenium login for user: {self.username}")
        
        system_type = self.config.get('emr.system_type', 'o19')
        
        if(system_type != 'opro'):
            driver.get(self.login_url)
        else:
            driver.get(self.login_url_pro)

        driver.implicitly_wait(10)

        # Locate the login fields and enter credentials
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        if(system_type != 'opro'):
            if(system_type == 'o15'):
                pin_field = driver.find_element(By.NAME, "pin")
            else:
                pin_field = driver.find_element(By.NAME, "pin2")

            pin_field.send_keys(self.pin)

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        if(system_type != 'opro'):
            # Submit the login form
            pin_field.send_keys(Keys.RETURN)
        else:
            password_field.send_keys(Keys.RETURN)
        
        logger.debug("Login form submitted")

        return driver.current_url

    def login_with_requests(self):
        """
        Perform login using a requests session with exponential backoff retry.

        Sends a POST request to the login URL with credentials.

        :return: A tuple containing the session and a boolean indicating success.
        :rtype: Tuple[requests.Session, bool]
        """
        logger.info(f"Attempting requests login for user: {self.username}")
        session = requests.Session()
        retry_delay = self.initial_retry_delay

        for attempt in range(self.max_retries):
            try:
                response = session.post(
                    self.login_url,
                    data={
                        "username": self.username,
                        "password": self.password,
                        "pin": self.pin
                    },
                    verify=self.config.get('emr.verify-HTTPS'),
                    timeout=self.config.get('general_setting.timeout', 300)  # Add a timeout to prevent hanging indefinitely
                )
                login_successful = response.url != self.login_url
                logger.debug(f"Login {'successful' if login_successful else 'failed'}")
                return session, login_successful
            except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Max retries reached. Login failed.")
                    return session, False

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
