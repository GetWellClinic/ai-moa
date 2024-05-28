import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from login import Login
from pdf_processor import PdfProcessor
from document_processor import DocumentProcessor

class OscarAutomation:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.username = self.config['user_login']['username']
        self.password = self.config['user_login']['password']
        self.pin = self.config['user_login']['pin']
        self.base_url = self.config['base_url']
        self.last_processed_pdf = self.config['last_processed_pdf']
        self.enable_ocr_gpu = self.config['enable_ocr_gpu']
        self.session = requests.Session()
        response = self.session.post(f"{self.base_url}/login.do", data={"username": self.username, "password": self.password, "pin": self.pin})
        
        if response.url == f"{self.base_url}/login.do":
            print("Login failed.")
        else:
            print("Login successful!")

    def load_config(self, filename):
        with open(filename, 'r') as file:
            config = json.load(file)
        return config

    def save_config(self, config):
        with open('config_file', 'w') as file:
            json.dump(config, file, indent=4)

    def login_successful_callback(self, driver):
        login_url = f"{self.base_url}/login.do"
        return self.login.login(driver, login_url)

    def process_pdfs(self):
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        self.login = Login(self.username, self.password, self.pin, self.base_url)
        self.pdf_processor = PdfProcessor(self.base_url, self.session, self.last_processed_pdf,self.enable_ocr_gpu)
        self.config["last_processed_pdf"] = self.pdf_processor.process_pdfs(driver, f"{self.base_url}/login.do", self.login_successful_callback)
        self.save_config(self.config)
        driver.quit()

    def process_documents(self):
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        self.login = Login(self.username, self.password, self.pin, self.base_url)
        self.document_processor = DocumentProcessor(self.base_url, self.session)
        self.config["last_processed_pdf"] = self.document_processor.process_documents(driver, f"{self.base_url}/login.do", self.login_successful_callback)

        driver.quit()

if __name__ == "__main__":
    oscar = OscarAutomation()
    oscar.process_pdfs()
    # oscar.process_documents()
