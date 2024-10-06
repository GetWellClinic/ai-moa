import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from utils.config_loader import load_config, save_config
from utils.logging_setup import setup_logging
from models.login import Login
from processors.pdf_processor import PdfProcessor
from processors.document_processor import DocumentProcessor
from processors.workflow_processor import WorkflowProcessor

class OscarAutomation:
    def __init__(self, config_file='config/config.yaml'):
        self.config = load_config(config_file)
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        self.username = self.config['user_login']['username']
        self.password = self.config['user_login']['password']
        self.pin = self.config['user_login']['pin']
        self.base_url = self.config['base_url']
        self.last_processed_pdf = self.config['last_processed_pdf']
        self.last_pending_doc_file = self.config['last_pending_doc_file']
        self.enable_ocr_gpu = self.config['enable_ocr_gpu']
        self.workflow_file = self.config.get('workflow_file', 'workflow.csv')
        self.session = requests.Session()
        self.login = Login(self.username, self.password, self.pin, self.base_url)
        self._login()

    def _login(self):
        response = self.session.post(f"{self.base_url}/login.do", data={
            "username": self.username,
            "password": self.password,
            "pin": self.pin
        })
        
        if response.url == f"{self.base_url}/login.do":
            self.logger.error("Login failed.")
        else:
            self.logger.info("Login successful!")

    def login_successful_callback(self, driver):
        return self.login.login(driver, f"{self.base_url}/login.do")

    def process_pdfs(self):
        self.logger.info("Starting PDF processing")
        with self._get_driver() as driver:
            pdf_processor = PdfProcessor(self.base_url, self.session, self.last_processed_pdf, self.enable_ocr_gpu)
            self.config["last_processed_pdf"] = pdf_processor.process_pdfs(driver, f"{self.base_url}/login.do", self.login_successful_callback)
            save_config(self.config)
        self.logger.info("PDF processing completed")

    def process_documents(self):
        self.logger.info("Starting document processing")
        with self._get_driver() as driver:
            document_processor = DocumentProcessor(self.base_url, self.session, self.last_pending_doc_file, self.enable_ocr_gpu)
            self.config["last_pending_doc_file"] = document_processor.process_documents(driver, f"{self.base_url}/login.do", self.login_successful_callback)
            save_config(self.config)
        self.logger.info("Document processing completed")

    def _get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def process_workflow(self):
        self.logger.info("Starting workflow processing")
        with self._get_driver() as driver:
            workflow_processor = WorkflowProcessor(self.workflow_file, self.session, self.base_url, self.enable_ocr_gpu)
            workflow_processor.process_workflow(driver, f"{self.base_url}/login.do", self.login_successful_callback)
        self.logger.info("Workflow processing completed")

if __name__ == "__main__":
    oscar = OscarAutomation()
    oscar.process_documents()
    oscar.process_pdfs()
    oscar.process_workflow()
