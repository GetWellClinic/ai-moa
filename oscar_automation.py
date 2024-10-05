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
        self.last_pending_doc_file = self.config['last_pending_doc_file']
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
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)

    def login_successful_callback(self, driver):
        login_url = f"{self.base_url}/login.do"
        return self.login.login(driver, login_url)

    def process_documents(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.login = Login(self.username, self.password, self.pin, self.base_url)
            self.document_processor = DocumentProcessor(self.base_url, self.session, self.last_pending_doc_file, self.enable_ocr_gpu)
            new_last_pending_doc_file = self.document_processor.process_documents(driver, f"{self.base_url}/login.do", self.login_successful_callback)
            
            if new_last_pending_doc_file is not None:
                self.config["last_pending_doc_file"] = new_last_pending_doc_file
                self.save_config(self.config)
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
