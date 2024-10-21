import yaml
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import logging

logger = logging.getLogger(__name__)
from auth.login_manager import LoginManager

class ProviderListManager:
    def __init__(self, workflow):
        self.config = workflow.config
        self.username = workflow.config.get('emr.username')
        self.password = workflow.config.get('emr.password')
        self.pin = workflow.config.get('emr.pin')
        self.base_url = workflow.config.get('emr.base_url')
        self.logger = workflow.logger
        self.session = requests.Session()
        self.login()

    def login(self) -> None:
        response = self.session.post(f"{self.base_url}/login.do",
                                     data={"username": self.username, "password": self.password, "pin": self.pin})
        if response.url == f"{self.base_url}/login.do":
            self.logger.info("Login failed.")
        else:
            self.logger.info("Login successful!")

    def upload_template_file(self) -> bool:
        url = f"{self.base_url}/oscarReport/reportByTemplate/uploadTemplates.do"
        template_file = self.config.get('provider_list.template_file', 'config/template_providerlist.txt')
        try:
            with open(template_file, 'rb') as file:
                files = {'templateFile': (template_file, file, 'text/plain')}
                data = {'action': 'add'}
                response = self.session.post(url, files=files, data=data)
                if(response.status_code == 200):
                    self.logger.info("Template uploaded successfully.")
                    return True
        except FileNotFoundError:
            self.logger.error(f"Template file not found: {template_file}")
            return False
        except requests.RequestException as e:
            self.logger.error(f"Error uploading template file: {e}")
            return False

    def check_template_file(self) -> None:

        url = f"{self.base_url}/oscarReport/reportByTemplate/homePage.jsp?templates=all"

        # Send the POST request
        response = self.session.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        tbody = soup.find('tbody', id='tableData')

        if tbody:
            # Extract rows from the tbody
            rows = tbody.find_all('tr')

            for row in rows:
                # Extract cells from the row
                cells = row.find_all('td')
                cell_values = [cell.get_text(strip=True) for cell in cells]
                if(cell_values[1] == "AI-MOA Config Search Providers (System generated)"):
                    self.logger.info("Template already exists.")
                    return True

        if(self.upload_template_file()):
            self.logger.info("Template uploaded.")
            return True
        else:
            self.logger.info("Template not uploaded.")
            return False



    def generate_provider_list(self) -> None:
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        login_manager = LoginManager(self.config)
        
        if self.check_template_file():
            url = f"{self.base_url}/oscarReport/reportByTemplate/homePage.jsp?templates=all"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            tbody = soup.find('tbody', id='tableData')
            template_id = self.find_template_id(tbody)
            
            if template_id:
                provider_data = self.fetch_provider_data(template_id)
                self.save_provider_list(provider_data)
            else:
                self.logger.info("Template id not found")
        
        driver.quit()

    def find_template_id(self, tbody: BeautifulSoup) -> Optional[str]:
        if tbody:
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if cells[1].get_text(strip=True) == "AI-MOA Config Search Providers (System generated)":
                    return cells[3].get('id')
        return None

    def fetch_provider_data(self, template_id: str) -> Optional[str]:
        url = f"{self.base_url}/oscarReport/reportByTemplate/GenerateReportAction.do"
        params = {"templateId": template_id, "submitButton": "Run Query"}
        try:
            response = self.session.post(url, data=params)
            soup = BeautifulSoup(response.text, 'html.parser')
            input_element = soup.find('input', {'type': 'hidden', 'class': 'btn', 'name': 'csv'})
            if input_element:
                self.logger.info("Fetching provider data.")
                return input_element.get('value').replace('"', '')
        except requests.RequestException as e:
            self.logger.info(f"Error fetching provider data: {e}")
        return None

    def save_provider_list(self, provider_data: Optional[str]) -> None:
        if provider_data:
            providers: List[Dict[str, str]] = []
            for row in provider_data.split('\n')[1:]:  # Skip header row
                fields = row.split(',')
                if len(fields) >= 3:
                    providers.append({
                        'last_name': fields[0],
                        'first_name': fields[1],
                        'provider_no': fields[2]
                    })
            
            provider_list = {'providers': providers}
            try:
                output_file = self.config.get('provider_list.output_file', 'config/provider_list.yaml')
                self.logger.info("Saving provider details to yaml file.")
                with open(output_file, 'w') as file:
                    yaml.dump(provider_list, file, default_flow_style=False)
                self.logger.info('Provider list has been saved to config/provider_list.yaml')
            except IOError as e:
                self.logger.error(f"Error saving provider list: {e}")
        else:
            self.logger.info('No provider data to save')

