"""
Module Name: emr_workflow.py

Description:
    This module manages the execution of the EMR workflow.
    It handles the processing of documents through various steps, utilizing AI prompts and interactions with the EMR system.

Author:
    Spring Health Corporation

License:
    Refer to the LICENSE file for detailed licensing information.
"""

from typing import Dict, Any, List
from huey import crontab, task
from config import ConfigManager
from logging import setup_logging
import os
import csv
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup
import fitz
import PyPDF2
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import torch

class Workflow:
    """
    Manages the execution of the EMR workflow.

    This class handles the processing of documents through various steps, utilizing AI prompts and interactions with the EMR system.

    :param config: Configuration manager containing workflow settings.
    :type config: ConfigManager
    :ivar logger: Logger instance for logging workflow activities.
    :vartype logger: logging.Logger
    :ivar task_results: Stores the results of each task executed in the workflow.
    :vartype task_results: dict
    """
    def __init__(self, config: ConfigManager):
        """
        Initializes the Workflow with configuration settings.

        :param config: Configuration manager containing workflow settings.
        :type config: ConfigManager
        """
        self.config = config
        self.logger = setup_logging(config)
        self.task_results = {}
        self.steps = config.workflow_steps
        self.document_categories = config.document_categories
        self.ai_prompts = config.ai_prompts
        self.patient_name = ''
        self.fl_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.document_description = ''
        self.filepath = config.get('document_processor.local.input_directory', '/app/input')
        self.tesseracted_text = None
        self.session = requests.Session()
        self.base_url = config.get('emr.base_url')
        self.file_name = ''
        self.enable_ocr_gpu = config.get('enable_ocr_gpu', False)
        self.url = config.get('ai.url', "http://127.0.0.1:5000/v1/chat/completions")
        self.headers = {
            "Authorization": f"Bearer {config.get('ai.api_key')}",
            "Content-Type": "application/json"
        }

    @task()
    def execute_task(self, step: Dict[str, Any]) -> Any:
        """
        Executes a single workflow task based on the provided step definition.

        :param step: A dictionary containing the task details.
        :type step: Dict[str, Any]
        :return: The result of the executed task.
        :rtype: Any
        """
        function_name = step['name']
        self.logger.info(f"Executing task: {function_name}")
        function_to_call = getattr(self, function_name, None)
        
        if function_to_call and callable(function_to_call):
            result = function_to_call()
            self.config.set_shared_state(step['name'], result)
            return result
        else:
            self.logger.error(f"Function {function_name} not found or not callable.")
            raise AttributeError(f"Function {function_name} not found or not callable.")
    def execute_task(self, step: Dict[str, Any]) -> Any:
        function_name = step['name']
        self.logger.info(f"Executing task: {function_name}")
        function_to_call = getattr(self, function_name, None)
        
        if function_to_call and callable(function_to_call):
            result = function_to_call()
            self.config.set_shared_state(step['name'], result)
            return result
        else:
            self.logger.error(f"Function {function_name} not found or not callable.")
            raise AttributeError(f"Function {function_name} not found or not callable.")

    def execute_workflow(self):
        """
        Executes the entire workflow as defined in the configuration.

        Navigates through each step, executing tasks and handling branching based on task results.
        """
        self.logger.info("Starting workflow execution")
        self.config.clear_shared_state()
        current_step = self.steps[0]
        while current_step:
            result = self.execute_task(current_step)
            
            if result:
                next_step_name = current_step['true_next']
            else:
                next_step_name = current_step['false_next']
            
            if next_step_name == 'exit':
                self.logger.info("Workflow execution completed")
                return
            
            current_step = next((step for step in self.steps if step['name'] == next_step_name), None)
        
        self.logger.info("Workflow execution completed")

    def check_for_file(self):
        input_directory = self.config.get('document_processor.local.input_directory', '/app/input')
        files = [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))]
        if files:
            self.config.set_shared_state('current_file', files[0])
            return True
        return False

    def has_ocr(self):
        pdf_path = os.path.join(self.filepath, self.config.get_shared_state('current_file'))
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

    def extract_text_from_pdf_file(self):
        text = ''
        pdf_path = os.path.join(self.filepath, self.config.get_shared_state('current_file'))
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text += page.extract_text()
            self.tesseracted_text = text
            return True
        except Exception as e:
            self.logger.error(f"An error occurred in extract_text_from_pdf_file: {e}")
            return False

    def extract_text_doctr(self):
        pdf_path = os.path.join(self.filepath, self.config.get_shared_state('current_file'))
        text = ''
        try:
            if self.enable_ocr_gpu:
                device = torch.device("cuda:0")
                model = ocr_predictor(pretrained=True).to(device)
            else:
                model = ocr_predictor(pretrained=True)
            doc = DocumentFile.from_pdf(pdf_path)
            result = model(doc)
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        text += '\n'
                        for word in line.words:
                            text += word.value + ' '
            self.tesseracted_text = text
            return True
        except Exception as e:
            self.logger.error(f"An error occurred in extract_text_doctr: {e}")
            return False

    def build_prompt(self):
        prompt = self.ai_prompts.get('build_prompt', '')
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": f"Today's Date is : {datetime.datetime.now().date()}\n{self.tesseracted_text}\n. {prompt}"
                }
            ],
            "mode": "instruct",
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        content_value = response.json()['choices'][0]['message']['content']
        self.logger.info(f"AI Response: {content_value}")
        self.find_category_index(content_value)
        return True

    def get_document_description(self, prompt):
        result = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.document_description = result
        self.config.set_shared_state('document_description', result)
        return True

    def getProviderList(self):
        prompt = self.ai_prompts.get('getProviderList', '')
        provider_list = self.getProviderListFromOscarFileMode()
        if provider_list is None:
            self.provider_number.append(99)
            return True
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": self.tesseracted_text + prompt + str(provider_list)
                }
            ],
            "mode": "instruct",
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        content_value = response.json()['choices'][0]['message']['content']
        match = re.search(r'\b\d+\b', content_value)
        if match:
            numerical_value = int(match.group())
            self.provider_number.append(numerical_value)
        else:
            self.provider_number.append(99)
        self.config.set_shared_state('provider_list', self.provider_number)
        return True

    def get_patient_name(self, prompt):
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        if '.' in name:
            name = name.replace('.', '')
        url = f"{self.base_url}/demographic/SearchDemographic.do"
        payload = {
            "query": "%"+name+"%"
        }
        response = self.session.post(url, data=payload)
        response_data = json.loads(response.text)
        if len(response_data["results"]) == 0:
            return False
        else:
            return True, response_data["results"]

    def set_patient(self, patient_data):
        self.patient_name = f"{patient_data['formattedName']} ({patient_data['formattedDob']})"
        self.fl_name = patient_data['formattedName']
        self.demographic_number = patient_data['demographicNo']
        if patient_data['providerNo'] is not None:
            self.mrp = patient_data['providerNo']
        self.config.set_shared_state('patient_name', self.patient_name)
        self.config.set_shared_state('demographic_number', self.demographic_number)
        self.config.set_shared_state('mrp', self.mrp)
        return True

    def get_doctor_name(self, prompt):
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        if '.' in name:
            name = name.replace('.', '')
        url = f"{self.base_url}/provider/SearchProvider.do"
        payload = {
            "query": name
        }
        response = self.session.post(url, data=payload)
        response_data = json.loads(response.text)
        if len(response_data["results"]) != 0:
            return True, response_data["results"]
        else:
            return False

    def set_doctor(self, provider_data):
        for item in provider_data:
            if isinstance(item, dict) and 'providerNo' in item:
                self.provider_number.append(item['providerNo'])
        self.config.set_shared_state('provider_list', self.provider_number)
        return True

    def o19_update(self):
        self.logger.info("================ Document Details ================")
        self.logger.info(f"Patient Name : {self.patient_name}")
        self.logger.info(f"Demographic Number : {self.demographic_number}")
        self.logger.info(f"Provider Number : {self.provider_number}")
        self.logger.info(f"Document Type : {self.fileType}")
        self.logger.info(f"Document Description : {self.document_description}")
        self.logger.info("================ End of Document Details ================")

        url = f"{self.base_url}/dms/ManageDocument.do"
        params = {
            "method": "documentUpdateAjax",
            "documentId": self.file_name,
            "docType": self.fileType,
            "documentDescription": self.document_description,
            "observationDate": str(datetime.datetime.now().date()),
            "demog": self.demographic_number,
            "demofindName": self.fl_name,
            "demoName": self.fl_name,
            "demographicKeyword": self.patient_name
        }

        params["flagproviders"] = []
        self.provider_number.append(127)
        for value in self.provider_number:
            params["flagproviders"].append(value)

        response = self.session.post(url, data=params)
        if response.status_code == 200:
            self.logger.info("Document updated successfully in O19")
            return True
        else:
            self.logger.error(f"Failed to update document in O19. Status code: {response.status_code}")
            return False
    def find_category_index(self, text):
        if '.' in text:
            text = text.replace('.', '')
        for word in text.split():
            for index, category in enumerate(self.document_categories):
                if '"' in word:
                    word = word.replace('"', '')
                if "'" in word:
                    word = word.replace("'", "")
                if word.lower() == category.lower():
                    self.fileType = category.lower()
                    self.execute_tasks_from_csv(index)
                    return True
        self.fileType = 'others'
        self.execute_tasks_from_csv(7)
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
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()['choices'][0]['message']['content']

    def getProviderList(self, prompt):
        provider_list = self.getProviderListFromOscarFileMode()
        if provider_list is None:
            self.provider_number.append(99)
            return True
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": self.tesseracted_text + prompt + str(provider_list)
                }
            ],
            "mode": "instruct",
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        content_value = response.json()['choices'][0]['message']['content']
        match = re.search(r'\b\d+\b', content_value)
        if match:
            numerical_value = int(match.group())
            self.provider_number.append(numerical_value)
        else:
            self.provider_number.append(99)
        self.config.set_shared_state('provider_list', self.provider_number)
        return True

    def getProviderListFromOscarFileMode(self):
        file_path = 'providers.csv'
        data = []
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    transformed_row = {
                        "lastname": row["last_name"], 
                        "firstname": row["first_name"],    
                        "provider_number": int(row["provider_no"]) 
                    }
                    data.append(transformed_row)
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
        except IOError as e:
            self.logger.error(f"Error reading the file: {e}")
        return data
