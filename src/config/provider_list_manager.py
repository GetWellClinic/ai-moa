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

import yaml
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import logging

logger = logging.getLogger(__name__)

class ProviderListManager:
    """
    Manages the provider list generation, template file upload, and fetching provider data from an EMR system.

    This class handles login, template file upload, verification, and the generation of provider lists
    by interacting with the EMR system through HTTP requests and web scraping techniques using BeautifulSoup.
    It also handles the saving of the generated provider list to a YAML file.

    Attributes:
        config (dict): The configuration settings for the workflow, including login credentials and URLs.
        username (str): The EMR username.
        password (str): The EMR password.
        pin (str): The EMR PIN.
        base_url (str): The base URL of the EMR system.
        logger (logging.Logger): A logger instance to log information and errors.
        session (requests.Session): The requests session for making HTTP requests.
    """
    def __init__(self, workflow):
        """
        Initializes the ProviderListManager with configuration and login credentials.

        Args:
            workflow (object): The workflow object that contains configuration data and logger instance.
        """
        self.config = workflow.config
        self.username = workflow.config.get('emr.username')
        self.password = workflow.config.get('emr.password')
        self.pin = workflow.config.get('emr.pin')
        self.base_url = workflow.config.get('emr.base_url')
        self.logger = workflow.logger
        self.system_type = workflow.config.get('emr.system_type')
        self.chrome_headless = workflow.config.get('chrome.options.headless')
        self.verify_https = workflow.config.get('emr.verify-HTTPS')
        
        self.headers = {}
        self.origin_url = ''

        pattern = r'^(https?://[^/]+)'
        match = re.match(pattern, self.base_url)

        if match:
            base_url = match.group(1)
            self.origin_url = base_url
        else:
            self.logger.info(f"Base url format issue, please cross check base url!")
            self.origin_url = self.base_url

        self.headers['Origin'] = self.origin_url
        self.headers['Referer'] = self.base_url

        self.session = workflow.session

    def upload_template_file(self) -> bool:
        """
        Uploads the provider list template file to the EMR system.

        Attempts to upload the template file specified in the configuration. If the upload is successful,
        logs the success and returns `True`. If there is an error or the file is not found, logs an error and
        returns `False`.

        Returns:
            bool: `True` if the file was uploaded successfully, otherwise `False`.

        Raises:
            requests.RequestException: If there is an error during the file upload.
            FileNotFoundError: If the template file is not found.
        """
        url = f"{self.base_url}/oscarReport/reportByTemplate/uploadTemplates.do"
        template_file = self.config.get('provider_list.template_file', 'template_providerlist.txt')
        try:
            with open(template_file, 'rb') as file:
                files = {'templateFile': (template_file, file, 'text/plain')}
                data = {'action': 'add'}
                self.headers['Referer'] = url
                self.session.headers.update(self.headers)
                response = self.session.post(url, files=files, data=data, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))
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
        """
        Checks if the provider list template file already exists in the EMR system.

        This method checks if a template file with the name "AI-MOA Config Search Providers (System generated)"
        exists in the system. If the template exists, it logs that the template already exists. If not, it attempts
        to upload the template file.

        Returns:
            bool: `True` if the template exists or was successfully uploaded, otherwise `False`.
        """
        url = f"{self.base_url}/oscarReport/reportByTemplate/homePage.jsp?templates=all"

        self.headers['Referer'] = url
        self.session.headers.update(self.headers)

        # Send the POST request
        response = self.session.get(url, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

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
        """
        Generates the provider list by fetching provider data from the EMR system.

        This method first checks if the provider list template file exists or uploads it if necessary. Then,
        it retrieves the provider data by sending a request with the template ID and parses the response.
        The data is saved in a YAML file.

        Returns:
            None
        """
        if self.check_template_file():
            url = f"{self.base_url}/oscarReport/reportByTemplate/homePage.jsp?templates=all"
            self.headers['Referer'] = url
            self.session.headers.update(self.headers)
            response = self.session.get(url, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))
            soup = BeautifulSoup(response.text, 'html.parser')
            tbody = soup.find('tbody', id='tableData')
            template_id = self.find_template_id(tbody)
            
            if template_id:
                provider_data = self.fetch_provider_data(template_id)
                self.save_provider_list(provider_data)
            else:
                self.logger.info("Template id not found")
        
        self.session.close()

    def find_template_id(self, tbody: BeautifulSoup) -> Optional[str]:
        """
        Finds the template ID for the provider list template.

        Args:
            tbody (BeautifulSoup): The BeautifulSoup object representing the HTML table body.

        Returns:
            Optional[str]: The template ID if found, otherwise `None`.
        """
        if tbody:
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if cells[1].get_text(strip=True) == "AI-MOA Config Search Providers (System generated)":
                    return cells[3].get('id')
        return None

    def fetch_provider_data(self, template_id: str) -> Optional[str]:
        """
        Fetches provider data from the EMR system by submitting the template ID.

        Args:
            template_id (str): The template ID to be used in the request.

        Returns:
            Optional[str]: The CSV data for the provider list if successful, otherwise `None`.

        Raises:
            requests.RequestException: If there is an error while fetching the data.
        """
        url = f"{self.base_url}/oscarReport/reportByTemplate/GenerateReportAction.do"
        params = {"templateId": template_id, "submitButton": "Run Query"}
        try:
            self.headers['Referer'] = url
            self.session.headers.update(self.headers)
            response = self.session.post(url, data=params, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))
            soup = BeautifulSoup(response.text, 'html.parser')
            input_element = soup.find('input', {'type': 'hidden', 'class': 'btn', 'name': 'csv'})
            if input_element:
                self.logger.info("Fetching provider data.")
                return input_element.get('value').replace('"', '')
        except requests.RequestException as e:
            self.logger.info(f"Error fetching provider data: {e}")
        return None

    def save_provider_list(self, provider_data: Optional[str]) -> None:
        """
        Saves the fetched provider data to a YAML file.

        Args:
            provider_data (Optional[str]): The CSV data containing the provider information.

        Returns:
            None

        Raises:
            IOError: If there is an error writing the YAML file.
        """
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
                output_file = self.config.get('provider_list.output_file', '../config/provider_list.yaml')
                self.logger.info("Saving provider details to yaml file.")
                with open(output_file, 'w') as file:
                    yaml.dump(provider_list, file, default_flow_style=False)
                self.logger.info('Provider list has been saved to config/provider_list.yaml')
            except IOError as e:
                self.logger.error(f"Error saving provider list: {e}")
        else:
            self.logger.info('No provider data to save')
