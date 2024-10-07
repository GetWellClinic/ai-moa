from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Login:
    def __init__(self, username, password, pin, base_url):
        self.username = username
        self.password = password
        self.pin = pin
        self.base_url = base_url

    def login(self, driver, login_url):
        try:
            driver.get(login_url)
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            pin_field = driver.find_element(By.NAME, "pin")

            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            pin_field.send_keys(self.pin)
            pin_field.send_keys(Keys.RETURN)

            return driver.current_url
        except Exception as error:
            print(f"An error occurred during login: {error}")
            return login_url
