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

import csv
import re
import random
import torch
import fitz
import PyPDF2
import requests
import json
import datetime
import logging
import time
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from bs4 import BeautifulSoup
from PIL import Image
import io
import pytesseract

import os
import logging
from utils.config_manager import ConfigManager
from huey import task

class Workflow:
    """
    A class to manage the workflow of processing medical documents.

    This class handles various operations such as OCR, patient information extraction,
    and interaction with the Oscar EMR system using Huey for task queuing.

    Attributes:
        config (ConfigManager): Configuration manager instance.
        patient_name (str): Name of the patient.
        fileType (str): Type of the file being processed.
        demographic_number (str): Demographic number of the patient.
        mrp (str): Most Responsible Provider number.
        provider_number (list): List of provider numbers.
        document_description (str): Description of the document.
        session: Session object for making HTTP requests.
        logger (logging.Logger): Logger instance.
    """

    def __init__(self, session, config):
        """
        Initialize the Workflow instance.

        Args:
            session: Session object for making HTTP requests.
            config (ConfigManager): Configuration manager instance.
        """
        self.config = config
        self.patient_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.document_description = ''
        self.session = session
        self.logger = logging.getLogger(__name__)

    def find_category_index(self, text):
        """
        Find the category index for the given text.

        This method searches for a matching category in the text and sets the fileType accordingly.
        If no match is found, it sets the fileType to 'others'.

        Args:
            text (str): The text to search for a category.

        Returns:
            bool: True if a category was found, False otherwise.
        """
        self.logger.debug("Inside find_category_index")
        if '.' in text:
            text = text.replace('.', '')
        for word in text.split():
            word = word.replace('"', '').replace("'", "")
            for index, category in enumerate(self.categories_code):
                if word.lower() == category.lower():
                    self.logger.debug(f"Category index found: {index}")
                    self.fileType = category.lower()
                    self.execute_tasks_from_csv(index)
                    return True
        self.logger.debug("No category found, setting to 'others'")
        self.fileType = 'others'
        self.execute_tasks_from_csv(7)
        return False

    def has_ocr(self):
        """
        Check if the PDF file has an OCR layer.

        This method attempts to extract text from each page of the PDF.
        If any page contains text, it assumes the PDF has an OCR layer.

        Returns:
            bool: True if the PDF has an OCR layer, False otherwise.
        """
        pdf_path = self.filepath
        try:
            pdf_document = fitz.open(pdf_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    return True
            return False
        except Exception as e:
            self.logger.error(f"An error occurred in has_ocr: {e}")
            return False

    def extract_text_from_pdf(self):
        #pytesseract ocr
        pdf_path = self.filepath
        try:
            pdf_document = fitz.open(pdf_path)
            extracted_text = ''
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    image_text = pytesseract.image_to_string(image)
                    extracted_text += image_text + '\n'
            self.tesseracted_text = extracted_text
            return True
        except Exception as e:
            self.logger.error(f"An error occurred in extract_text_from_pdf: {e}")
            return False

    def extract_text_doctr(self):
        start_time = time.time()
        pdf_path = self.filepath
        self.logger.debug("Processing PDF: %s", pdf_path)
        try:
            device = torch.device("cuda:0" if self.enable_ocr_gpu and torch.cuda.is_available() else "cpu")
            model = ocr_predictor(pretrained=True).to(device)
            doc = DocumentFile.from_pdf(pdf_path)
            result = model(doc)
            
            text = self._process_ocr_result(result)
            self.tesseracted_text = text.strip()
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"OCR completed in {elapsed_time:.2f} seconds")
            return True
        except Exception as e:
            self.logger.exception(f"Error in extract_text_doctr: {e}")
            return False

    def _process_ocr_result(self, result):
        text = []
        for page in result.pages:
            self.logger.debug("Processing page %d", page.page_idx)
            page_text = []
            for block in page.blocks:
                for line in block.lines:
                    page_text.append(' '.join(word.value for word in line.words))
            text.append('\n'.join(page_text))
        return '\n\n'.join(text)

    def extract_text_from_pdf_file(self):
        #if pdf has ocr get the text, no need to use doctr ocr
        text = ''
        pdf_path = self.filepath
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                for page_num in range(num_pages):  # Iterate over all pages
                    page = reader.pages[page_num]
                    text += page.extract_text()
            self.tesseracted_text = text
            return True
        except Exception as e:
            self.logger.error(f"An error occurred in extract_text_from_pdf_file: {e}")
            return False

    def build_prompt(self, prompt):
        data = self._prepare_prompt_data(prompt)
        try:
            return self._send_prompt_request(data)
        except requests.RequestException as e:
            self.logger.error(f"Error in build_prompt: {e}")
            return False

    def _prepare_prompt_data(self, prompt):
        return {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": f"{self.tesseracted_text}. {prompt}"}
            ],
            "mode": "instruct",
            "temperature": self.config.get('ai_config', {}).get('temperature', 0.1),
            "character": "Assistant",
            "top_p": self.config.get('ai_config', {}).get('top_p', 0.1)
        }

    def _send_prompt_request(self, data):
        response = requests.post(self.url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        content_value = response.json()['choices'][0]['message']['content']
        self.logger.debug("LLM response content: %s", content_value)
        self.find_category_index(content_value)
        return True

    def build_sub_prompt(self, prompt):
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "mode": "instruct",
            "temperature": self.config.get('ai_config', {}).get('temperature', 0.1),
            "character": "Assistant",
            "top_p": self.config.get('ai_config', {}).get('top_p', 0.1)
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()['choices'][0]['message']['content']

    def get_patient_name(self, prompt):
        self.logger.debug("Getting patient name")
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        if '.' in name:
            name = name.replace('.', '')
        self.logger.debug("Patient name: %s", name)
        url = f"{self.base_url}/demographic/SearchDemographic.do"

        payload = {
            "query": f"%{name}%"
        }

        self.logger.debug("Sending POST request to search for patient")
        response = self.session.post(url, data=payload)
        self.logger.debug("Response text: %s", response.text)

        response_data = json.loads(response.text)

        if len(response_data["results"]) == 0:
            self.logger.info("No patient found")
            return False
        else:
            self.logger.info("Patient(s) found")
            return True, response_data["results"]

    def set_doctor_from_code(self, name):
        self.logger.debug("Setting doctor from code: %s", name)
        oscar_response = []
        if name:
            if '.' in name:
                name = name.replace('.', '')

            url = f"{self.base_url}/provider/SearchProvider.do"

            payload = {
                "query": name
            }

            self.logger.debug("Sending POST request to search for provider")
            response = self.session.post(url, data=payload)

            self.logger.debug("Provider search response: %s", response.text)

            data = json.loads(response.text)

            for item in data["results"]:
                self.logger.debug("Processing item: %s", item)
                if isinstance(item, dict):
                    if 'providerNo' in item:
                        self.logger.debug("Provider number: %s", item['providerNo'])
                        self.provider_number.append(item['providerNo'])
                        self.logger.debug(f"Provider number added: {item['providerNo']}")
            self.logger.debug(f"Provider numbers: {self.provider_number}")

            if self.provider_number:
                return True
            else:
                return False

    def get_doctor_name(self, prompt):
        self.logger.debug("Getting doctor name")
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.logger.debug("Doctor name: %s", name)
        oscar_response = []
        if name:
            if '.' in name:
                name = name.replace('.', '')

            url = f"{self.base_url}/provider/SearchProvider.do"

            payload = {
                "query": name
            }

            self.logger.debug("Sending POST request to search for provider")
            response = self.session.post(url, data=payload)

            self.logger.debug("Provider search response: %s", response.text)

            response_data = json.loads(response.text)

            if len(response_data["results"]) != 0:
                results = response_data["results"]
                if isinstance(results, list):
                    for item in results:
                        if isinstance(item, dict):
                            oscar_response.append(item)

            if len(oscar_response) != 0:
                self.logger.info("Provider(s) found")
                return True, oscar_response
            else:
                return False

    def get_document_description(self, prompt):
        result = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.logger.debug(f"Document description: {result}")
        self.document_description = result
        return True

    def filter_results(self, prompt, additional_param=None):
        if additional_param is not None:
            self.logger.debug("Filtering results")
            details = self.build_sub_prompt(self.tesseracted_text + prompt + str(additional_param))
            self.logger.debug("Filtered results: %s", details)
            return True, details
        else:
            return False

    def set_patient(self, additional_param=None):
        self.logger.debug("Setting patient")
        if additional_param is not None:
            self.logger.debug("Additional param: %s", additional_param)
            try:
                data = json.loads(additional_param)
                self.patient_name = f"{data['formattedName']}({data['formattedDob']})"
                self.fl_name = data['formattedName']
                self.demographic_number = data['demographicNo']
                if data['providerNo'] is not None:
                    self.mrp = data['providerNo']
                self.logger.info(f"Patient set: {self.patient_name}")
                return True
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decoding error: {e}")
                return False
        else:
            self.logger.info("No additional param provided, skipping patient set")
            return False

    def set_doctor(self, additional_param=None):
        self.logger.debug("Setting doctor")
        if additional_param is not None:
            self.logger.debug("Additional param: %s", additional_param)
            data = json.loads(additional_param)
            self.logger.debug("Provider data: %s", data)
            for item in data:
                self.logger.debug("Processing item: %s", item)
                if isinstance(item, dict):
                    if 'providerNo' in item:
                        self.logger.debug("Provider number: %s", item['providerNo'])
                        self.provider_number.append(item['providerNo'])
            self.logger.debug("Provider numbers: %s", self.provider_number)
            return True
        else:
            self.logger.info(f"Doctor(s) set: {self.provider_number}")
            return True

    def patientSearch(self, prompt, type_of_query):
        self.logger.debug(f"Searching for patient with type: {type_of_query}")
        query = self._generate_patient_query(prompt)
        if not query:
            return False

        try:
            response = self._send_patient_search_request(query, type_of_query)
            return self._process_patient_search_response(response)
        except requests.RequestException as e:
            self.logger.error(f"Error in patientSearch: {e}")
            return False

    def _generate_patient_query(self, prompt):
        query = self.build_sub_prompt(f"{self.tesseracted_text} {prompt}")
        if not query:
            self.logger.info("No query generated from prompt")
            return None
        return query.replace('.', '')

    def _send_patient_search_request(self, query, type_of_query):
        url = f"{self.base_url}/demographic/demographiccontrol.jsp"
        payload = {
            "search_mode": type_of_query,
            "keyword": query,
            "orderby": ["last_name", "first_name"],
            "dboperation": "search_titlename",
            "limit1": 0,
            "limit2": 10,
            "displaymode": "Search",
            "ptstatus": "active",
            "fromMessenger": "False",
            "outofdomain": ""
        }
        response = self.session.post(url, data=payload, timeout=30)
        response.raise_for_status()
        return response

    def _process_patient_search_response(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all(class_=["odd", "even"])
        if table:
            self.logger.debug("Patient search results found")
            return True, str(table)
        else:
            self.logger.info("No patient search results found")
            return False

    def getProviderList(self, prompt):
        self.logger.debug("Getting provider list")
        url = f"{self.base_url}/admin/providersearchresults.jsp"
        payload = {
            "search_mode": "search_providerno",
            "search_status": "All",
            "keyword": "",
            "button": "",
            "orderby": "last_name",
            "limit1": 0,
            "limit2": 10000
        }

        try:
            response = self.session.post(url, data=payload, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'tblResults'})

            if table:
                oscar_response = self.build_sub_prompt(f"{prompt} {table}")
                self.logger.debug("Provider list retrieved")
                return True, oscar_response
            else:
                self.logger.info("No provider list found")
                return False
        except requests.RequestException as e:
            self.logger.error(f"Error in getProviderList: {e}")
            return False

    def oscar_update(self):
        self.logger.debug(f"Document Details: Patient: {self.patient_name}, Demographic: {self.demographic_number}, Providers: {self.provider_number}, Type: {self.fileType}, Description: {self.document_description}")
        self.logger.info("Updating Oscar")
        url = f"{self.base_url}/dms/ManageDocument.do"

        params = {
            "method": "addIncomingDocument",
            "pdfDir": "File",
            "pdfName": self.file_name,
            "queueId": "1",
            "pdfNo": "1",
            "queue": "1",
            "pdfAction": "",
            "lastdemographic_no": "1",
            "entryMode": "Fast",
            "docType": self.fileType,
            "docClass": "",
            "docSubClass": "",
            "documentDescription": self.document_description,
            "observationDate": str(datetime.datetime.now().date()),
            "saved": "false",
            "demog": self.demographic_number,
            "demographicKeyword": self.patient_name,
            "provi": self.provider_number[0] if self.provider_number else "",
            "MRPNo": self.mrp,
            "MRPName": "undefined",
            "ProvKeyword": "",
            "save": "Save & Next",
            "flagproviders": self.provider_number + [127]  # Add provider 127 to all
        }

        self.logger.debug(f"Oscar update params: {params}")
        
        try:
            response = self.session.post(url, data=params, timeout=30)
            response.raise_for_status()
            self.logger.debug(f"Oscar update response status: {response.status_code}")
            self.logger.debug(f"Oscar update response: {response.text}")
            return True
        except requests.RequestException as e:
            self.logger.error(f"Error in oscar_update: {e}")
            return False

    @task()
    def execute_task(self, task, previous_result=None):
        task_number, function_name, *params, true_next_row, false_next_row = task
        self.logger.debug(f"Executing task {task_number}: {function_name}")
        function_to_call = getattr(self, function_name, None)
        
        if function_to_call and callable(function_to_call):
            self.logger.info(f"Executing Task {task_number} with function: {function_name} and parameters: {', '.join(params)}")
            
            if 'additional_param' in function_to_call.__code__.co_varnames:
                additional_param = previous_result if previous_result is not None else None
                response = function_to_call(*params, additional_param=additional_param)
            else:
                response = function_to_call(*params)

            self.logger.debug(f"Response from {function_name}: {response}")

            if isinstance(response, tuple) and len(response) > 1:
                if response[0]:
                    return true_next_row, response[1]
                else:
                    return false_next_row, response[1]
            else:
                return true_next_row if response else false_next_row 
        else:
            self.logger.error(f"Error: Function {function_name} not found or not callable.")
            return false_next_row 

    def execute_tasks(self, tasks, current_row, previous_result=None):
        if current_row >= len(tasks):
            self.logger.info("Reached end of tasks.")
            return

        next_row = self.execute_task(tasks[current_row], previous_result)
        if next_row == 'exit':
            self.logger.info("Exiting task execution.")
            return

        if isinstance(next_row, tuple): 
            next_row_index = int(next_row[0])
            next_result = next_row[1] if len(next_row) > 1 else None
            self.execute_tasks(tasks, next_row_index, previous_result=next_result)
        else:
            next_row_parts = next_row.split(",") if next_row else None
            if next_row_parts:
                next_row_index = int(next_row_parts[0])
                next_result = next_row_parts[1] if len(next_row_parts) > 1 else None
                self.execute_tasks(tasks, next_row_index, previous_result=next_result)

    def read_tasks_from_csv(self, file_path):
        tasks = []
        self.logger.debug(f"Reading tasks from CSV: {file_path}")
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                tasks.append(row)
        return tasks

    def execute_tasks_from_csv(self, index=None):
        if index is None:
            tasks = self.read_tasks_from_csv(self.config.get('workflow', {}).get('file_path', 'workflow.csv'))
        else:
            tasks = self.read_tasks_from_csv(f"{index}.csv")
        self.logger.debug(f"Processing file: {self.filepath}")
        self.execute_tasks(tasks, 0)

    def execute_workflow(self):
        self.logger.info("Executing workflow")
        current_step = self.workflow_config.workflow_steps[0]['name']
        while current_step != 'exit':
            self.logger.info(f"Executing step: {current_step}")
            result = self.execute_step(current_step)
            current_step = self.workflow_config.get_next_step(current_step, result)

    @task()
    def execute_step(self, step_name):
        function_to_call = getattr(self, step_name, None)
        if function_to_call and callable(function_to_call):
            try:
                result = function_to_call()
                self.logger.info(f"Step {step_name} completed with result: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error executing step {step_name}: {str(e)}")
                return False
        else:
            self.logger.error(f"Error: Function {step_name} not found or not callable.")
            return False
