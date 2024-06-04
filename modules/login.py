from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Login:
    """
    The Login class handles the login process for a web application.
    
    Attributes:
        username (str): The username for login.
        password (str): The password for login.
        pin (str): The PIN for login.
        base_url (str): The base URL of the application.
    """
    
    def __init__(self, username, password, pin, base_url):
        """
        Initializes the Login object with the provided username, password, pin, and base URL.

        Parameters:
            username (str): The username for login.
            password (str): The password for login.
            pin (str): The PIN for login.
            base_url (str): The base URL of the application.
        """
        self.username = username
        self.password = password
        self.pin = pin
        self.base_url = base_url

    def login(self, driver, login_url):
        """
        Automates the login process using Selenium WebDriver.

        Parameters:
            driver (WebDriver): The Selenium WebDriver instance.
            login_url (str): The URL of the login page.
        
        Returns:
            current_url (str): The URL of the current page after attempting to log in.

        Process:
            1. Navigate to the login URL.
            2. Locate the username, password, and pin input fields by their `name` attributes.
            3. Enter the provided username, password, and pin.
            4. Submit the login form.
            5. Return the current URL after attempting to log in.
        """
        driver.get(login_url)
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        pin_field = driver.find_element(By.NAME, "pin")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        pin_field.send_keys(self.pin)
        pin_field.send_keys(Keys.RETURN)

        current_url = driver.current_url
        return current_url
