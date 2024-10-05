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
import csv
import io
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from login import Login
from bs4 import BeautifulSoup

class OscarProviderList:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.username = self.config['user_login']['username']
        self.password = self.config['user_login']['password']
        self.pin = self.config['user_login']['pin']
        self.base_url = self.config['base_url']
        self.session = requests.Session()
        try:
            response = self.session.post(f"{self.base_url}/login.do", data={"username": self.username, "password": self.password, "pin": self.pin})
            response.raise_for_status()
            if response.url == f"{self.base_url}/login.do":
                print("Login failed.")
            else:
                print("Login successful!")
        except requests.RequestException as e:
            print(f"Login request failed: {e}")

    def load_config(self, filename):
        with open(filename, 'r') as file:
            config = json.load(file)
        return config

    def login_successful_callback(self, driver):
        login_url = f"{self.base_url}/login.do"
        return self.login.login(driver, login_url)

    def upload_template_file(self, driver, login_url):
        driver.get(login_url)
        current_url = self.login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            return False

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
                    print("Template already exists.")
                    return True
        
        url = f"{self.base_url}/oscarReport/reportByTemplate/uploadTemplates.do"

        template_file = 'template_providerlist.txt'

        files = {
                    'templateFile': (template_file, open(template_file, 'rb'), 'text/plain')
                }

        data = {
                    'action': 'add'
                }


        response = self.session.post(url, files=files, data=data)

        if response.status_code == 200:
            print('Template added to OSCAR successful')
            # print('Response content:', response.text)
            return True
        else:
            print(f'Failed to upload template file. Status code: {response.status_code}')
            print('Response content:', response.text)

        return False

    def generate_provider(self):
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        self.login = Login(self.username, self.password, self.pin, self.base_url)

        upload_template_file = self.upload_template_file(driver,f"{self.base_url}/login.do")

        if(upload_template_file == True):
            print("generate_provider_list")

            url = f"{self.base_url}/oscarReport/reportByTemplate/homePage.jsp?templates=all"

            # Send the POST request
            response = self.session.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            tbody = soup.find('tbody', id='tableData')

            template_id = 0

            if tbody:
                # Extract rows from the tbody
                rows = tbody.find_all('tr')

                for row in rows:
                    # Extract cells from the row
                    cells = row.find_all('td')
                    cell_values = [cell.get_text(strip=True) for cell in cells]
                    cell_id = [cell.get("id") for cell in cells]
                    if(cell_values[1] == "AI-MOA Config Search Providers (System generated)"):
                        template_id = cell_id[3]

            if(template_id == 0):
                print("Template id cant be zero")
                return

            url = f"{self.base_url}/oscarReport/reportByTemplate/GenerateReportAction.do"
            
            params =  {
                "templateId": template_id,
                "submitButton": "Run Query"
            }

            # Send the POST request
            response = self.session.post(url,data=params)

            soup = BeautifulSoup(response.text, 'html.parser')

            input_element = soup.find('input', {'type': 'hidden', 'class': 'btn', 'name': 'csv'})

            if input_element:

                cleaned_string = input_element.get('value').replace('"', '')

                csv_file = io.StringIO(cleaned_string)

                data = list(csv.reader(csv_file))

                # print(data)

                csv_file_path = 'providers.csv'

                # Write data to CSV file
                with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
    
                    # Write the data
                    writer.writerows(data)

                print(f'Data has been written to {csv_file_path}')
            else:
                print('List not found')

            

        driver.quit()

if __name__ == "__main__":
    oscarPL = OscarProviderList()
    oscarPL.generate_provider()
