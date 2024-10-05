import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.processors.document_processor import DocumentProcessor
from src.utils.config import load_config, save_config
from src.utils.login import Login

class OscarAutomation:
    def __init__(self, config_file='config_main.json'):
        self.config = load_config(config_file)
        self.username = self.config['user_login']['username']
        self.password = self.config['user_login']['password']
        self.pin = self.config['user_login']['pin']
        self.base_url = self.config['base_url']
        self.last_processed_pdf = self.config['last_processed_pdf']
        self.last_pending_doc_file = self.config['last_pending_doc_file']
        self.enable_ocr_gpu = self.config['enable_ocr_gpu']
        self.session = requests.Session()
        response = self.session.post(f"{self.base_url}/login.do", data={"username": self.username, "password": self.password, "pin": self.pin})
        
        if response.url == f"{self.base_url}/login.do":
            print("Login failed.")
        else:
            print("Login successful!")

    def login_successful_callback(self, driver):
        login_url = f"{self.base_url}/login.do"
        return self.login.login(driver, login_url)

    def process_documents(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.login = Login(self.username, self.password, self.pin, self.base_url)
            self.document_processor = DocumentProcessor(self.base_url, self.session, self.last_pending_doc_file, self.enable_ocr_gpu)
            new_last_pending_doc_file = self.document_processor.process_documents(driver, f"{self.base_url}/login.do", self.login_successful_callback)
            
            if new_last_pending_doc_file is not None:
                self.config["last_pending_doc_file"] = new_last_pending_doc_file
                save_config(self.config)
            else:
                print("Document processing failed or no new documents were processed.")
        except Exception as e:
            print(f"An error occurred during document processing: {e}")
        finally:
            if 'driver' in locals():
                driver.quit()

if __name__ == "__main__":
    oscar = OscarAutomation()
    oscar.process_documents()
