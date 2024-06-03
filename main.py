import json
import requests
import argparse
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from login import Login
from pdf_processor import PdfProcessor
from document_processor import DocumentProcessor

class MOAAutomation:
    """
    MOAAutomation handles the automation tasks for the MOA system, including logging in, 
    processing PDFs, and processing documents.
    """

    def __init__(self, config_file='config.json'):
        """
        Initializes the MOAAutomation object by loading the configuration file and 
        performing a login operation.

        Args:
            config_file (str): Path to the configuration file (default is 'config.json')
        """
        self.config = self.load_config(config_file)
        self.username = self.config['user_login']['username']
        self.password = self.config['user_login']['password']
        self.pin = self.config['user_login']['pin']
        self.base_url = self.config['base_url']
        self.last_processed_pdf = self.config['last_processed_pdf']
        self.session = requests.Session()
        
        response = self.session.post(
            f"{self.base_url}/login.do",
            data={"username": self.username, "password": self.password, "pin": self.pin}
        )

        if response.url == f"{self.base_url}/login.do":
            print("Login failed.")
        else:
            print("Login successful!")

    @staticmethod
    def load_config(filename):
        """
        Loads the configuration file.

        Args:
            filename (str): Path to the configuration file

        Returns:
            dict: Parsed configuration as a dictionary
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Configuration file {filename} does not exist.")
        
        with open(filename, 'r') as file:
            config = json.load(file)
        return config

    @staticmethod
    def save_config(config, filename='config.json'):
        """
        Saves the configuration to a file.

        Args:
            config (dict): Configuration dictionary to save
            filename (str): Path to the configuration file (default is 'config.json')
        """
        with open(filename, 'w') as file:
            json.dump(config, file, indent=4)

    def login_successful_callback(self, driver):
        """
        Callback function to handle login success in Selenium.

        Args:
            driver (webdriver.Chrome): Selenium WebDriver instance

        Returns:
            bool: Result of the login operation
        """
        login_url = f"{self.base_url}/login.do"
        return self.login.login(driver, login_url)

    def process_pdfs(self, dry_run=False, dry_run_path=None):
        """
        Processes PDFs using the PdfProcessor. If dry_run is True, it only lists the PDFs.

        Args:
            dry_run (bool): Indicates if this is a dry run
            dry_run_path (str): Path to the PDFs for the dry run
        """
        if dry_run:
            if not os.path.exists(dry_run_path):
                raise FileNotFoundError(f"The specified path for dry run {dry_run_path} does not exist.")
            print(f"Performing dry run with PDFs from {dry_run_path}")
            for pdf_file in os.listdir(dry_run_path):
                if pdf_file.endswith('.pdf'):
                    print(f"Found PDF: {pdf_file}")
            return

        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        self.login = Login(self.username, self.password, self.pin, self.base_url)
        self.pdf_processor = PdfProcessor(self.base_url, self.session, self.last_processed_pdf)
        self.config["last_processed_pdf"] = self.pdf_processor.process_pdfs(
            driver, f"{self.base_url}/login.do", self.login_successful_callback
        )
        self.save_config(self.config)
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description="MOA Automation Script")
    parser.add_argument('--config-file', type=str, default='config.json', help='Path to the configuration file')
    parser.add_argument('--dry-run', type=str, help='Path to the PDF files to process for dry run')

    args = parser.parse_args()

    # Validate configuration file
    if not os.path.exists(args.config_file):
        raise FileNotFoundError(f"Configuration file {args.config_file} does not exist.")

    # Create an instance of MOAAutomation
    oscar = MOAAutomation(config_file=args.config_file)

    # Check if dry run is specified
    if args.dry_run:
        oscar.process_pdfs(dry_run=True, dry_run_path=args.dry_run)
    else:
        oscar.process_pdfs()

if __name__ == "__main__":
    main()

