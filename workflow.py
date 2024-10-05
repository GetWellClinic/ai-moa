import csv
import datetime
import json
import logging
import os
import random
import re

import fitz
import PyPDF2
import requests
import torch
from bs4 import BeautifulSoup
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

from src.utils.logging_config import setup_logging

def load_config(config_file='config/config.json'):
    with open(config_file, 'r') as f:
        return json.load(f)

config = load_config()

logger = setup_logging()

class Workflow:
    def __init__(self, filepath, session, base_url, file_name):
        self.patient_name = ''
        self.fl_name = ''
        self.file_type = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.document_description = ''
        self.filepath = filepath
        self.tesseracted_text = None
        self.session = session
        self.base_url = base_url
        self.file_name = file_name
        self.enable_ocr_gpu = config['ocr']['enable_gpu']
        self.url = config['api']['url']
        self.headers = {
            "Authorization": f"Bearer {config['api']['auth_token']}",
            "Content-Type": "application/json"
        }
        self.categories = [
            "Lab", "Consult", "Insurance", "Legal", "Old Chart", "Radiology",
            "Pathology", "Others", "Photo", "Consent", "Diagnostics",
            "Pharmacy", "Requisition", "Referral", "Request"
        ]
        self.categories_code = [
            "Lab", "Consult", "Insurance", "Legal", "OldChart", "Radiology",
            "Pathology", "Others", "Photo", "Consent", "Diagnostics",
            "Pharmacy", "Requisition", "Referral", "Request"
        ]
        logger.info(f"Workflow initialized for file: {self.file_name}")

    def find_category_index(self, text):
        if '.' in text:
            text = text.replace('.', '')
        for index, category in enumerate(self.categories_code):
            for word in text.split():
                if word.lower() == category.lower():
                    logger.info(f"Category found: {category} (index: {index})")
                    self.file_type = category.lower()
                    self.execute_tasks_from_csv(index)
                    return True
        logger.info("No specific category found, defaulting to 'others'")
        self.file_type = 'others'
        self.execute_tasks_from_csv(7)

    def has_ocr(self):
        pdf_path = self.filepath
        try:
            pdf_document = fitz.open(pdf_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    logger.info("OCR text found in the PDF")
                    return True
            logger.info("No OCR text found in the PDF")
            return False
        except Exception as e:
            logger.error(f"An error occurred while checking for OCR: {e}")
            return False

    def extract_text_doctr(self):
        start_time = time.time()
        pdf_path = self.filepath
        text = ''
        try:
            if self.enable_ocr_gpu:
                device = torch.device("cuda:0")
                model = ocr_predictor(pretrained=True).to(device)
                logger.info("Using GPU for OCR")
            else:
                model = ocr_predictor(pretrained=True)
                logger.info("Using CPU for OCR")
            doc = DocumentFile.from_pdf(pdf_path)
            result = model(doc)
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        text += '\n'
                        for word in line.words:
                            text += word.value + ' '
            self.tesseracted_text = text
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"OCR completed. Time taken: {elapsed_time:.2f} seconds")
            return True
        except Exception as e:
            logger.error(f"An error occurred during OCR: {e}")
            logger.info(f"Removing problematic PDF: {pdf_path}")
            os.remove(pdf_path)
            return False

    def extract_text_from_pdf_file(self):
        text = ''
        pdf_path = self.filepath
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
            print(f"An error occurred: {e}")
            return False

    def build_prompt(self, prompt):
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": f"{self.tesseracted_text}. {prompt}"
                }
            ],
            "mode": "instruct",
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        print(response.json())
        content_value = response.json()['choices'][0]['message']['content']
        print(content_value)
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
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()['choices'][0]['message']['content']

    def get_patient_name(self, prompt):
        name = self.build_sub_prompt(f"{self.tesseracted_text}{prompt}")
        if '.' in name:
            name = name.replace('.', '')
        print(name)
        url = f"{self.base_url}/demographic/SearchDemographic.do"
        payload = {
            "query": name
        }
        response = self.session.post(url, data=payload)
        response_data = json.loads(response.text)
        if not response_data["results"]:
            return False
        return True, response_data["results"]

    def set_doctor_from_code(self, name):
        if name:
            if '.' in name:
                name = name.replace('.', '')
            url = f"{self.base_url}/provider/SearchProvider.do"
            payload = {
                "query": name
            }
            response = self.session.post(url, data=payload)
            data = json.loads(response.text)
            for item in data["results"]:
                if isinstance(item, dict) and 'providerNo' in item:
                    self.provider_number.append(item['providerNo'])
            return bool(self.provider_number)
        return False

    def get_doctor_name(self, prompt):
        name = self.build_sub_prompt(f"{self.tesseracted_text}{prompt}")
        print(name)
        oscar_response = []
        if name:
            if '.' in name:
                name = name.replace('.', '')
            url = f"{self.base_url}/provider/SearchProvider.do"
            payload = {
                "query": name
            }
            response = self.session.post(url, data=payload)
            response_data = json.loads(response.text)
            if response_data["results"]:
                results = response_data["results"]
                if isinstance(results, list):
                    oscar_response = [item for item in results if isinstance(item, dict)]
            if oscar_response:
                return True, oscar_response
        return False

    def get_document_description(self, prompt):
        result = self.build_sub_prompt(self.tesseracted_text + prompt)
        print(result)
        self.document_description = result
        return True

    def filter_results(self, prompt, additional_param=None):
        if additional_param is not None:
            details = self.build_sub_prompt(self.tesseracted_text + prompt + str(additional_param))
            return True, details
        else:
            return False

    def set_patient(self, additional_param=None):
        if additional_param is not None:
            data = json.loads(additional_param)
            self.patient_name = data[0]['formattedName'] + '(' + data[0]['fomattedDob'] + ')'
            self.demographic_number = data[0]['demographicNo']
            if data[0]['providerNo'] is not None:
                self.mrp = data[0]['providerNo']
            return True
        else:
            return False

    def set_doctor(self, additional_param=None):
        if additional_param is not None:
            data = json.loads(additional_param)
            print(data)
            for item in data:
                if isinstance(item, dict):
                    if 'providerNo' in item:
                        print(item['providerNo'])
                        self.provider_number.append(item['providerNo'])
            print(self.provider_number)
            return True
        else:
            return False

    def patientSearch(self, prompt, type_of_query):
        query = self.build_sub_prompt(f"{self.tesseracted_text}{prompt}")
        if "False" in query:
            return False
        parts = query.split(':')
        parts = [part.strip() for part in parts]
        if len(parts) > 1:
            query = parts[1]

        if type_of_query == "search_dob":
            pattern = r'\d{4}-\d{2}-\d{2}'
            match = re.search(pattern, query)
            if match:
                query = match.group()
                print(query)

        if type_of_query == "search_hin":
            pattern = r'\b\d+\b'
            match = re.search(pattern, query)
            if match:
                query = match.group()
                print(query)

        if query:
            query = query.replace('.', '').replace(',', '')
            table = self.getPatientHTML(type_of_query, query)

            if table:
                print(str(table))
                return True, str(table)

            if type_of_query == "search_name":
                parts = query.split(' is ')
                name_parts = parts[1].split() if len(parts) > 1 else query.split()
                
                all_combinations = list(itertools.permutations(name_parts))
                formatted_combinations = [f"%{combo[0]}%,%{'%'.join(combo[1:])}%" for combo in all_combinations]

                for combo in formatted_combinations:
                    print(combo)
                    table = self.getPatientHTML(type_of_query, combo)
                    if table:
                        print(str(table))
                        return True, str(table)
        return False

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
                    "content": f"{self.tesseracted_text}{prompt}{provider_list}"
                }
            ],
            "mode": "instruct",
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        content_value = response.json()['choices'][0]['message']['content']

        print(content_value)

        match = re.search(r'\b\d+\b', content_value)

        if match:
            numerical_value = int(match.group())
            self.provider_number.append(numerical_value)
        else:
            self.provider_number.append(99)

        return True

    def oscar_update(self):
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
            "docType": self.file_type,
            "docClass": "",
            "docSubClass": "",
            "documentDescription": self.document_description,
            "observationDate": str(datetime.datetime.now().date()),
            "saved": "false",
            "demog": "1",
            "demographicKeyword": self.patient_name,
            "provi": self.provider_number[0],
            "MRPNo": self.mrp,
            "MRPName": "undefined",
            "ProvKeyword": "",
            "save": "Save & Next"
        }
        params["flagproviders"] = self.provider_number.copy()
        self.session.post(url, data=params)
        return True

    def execute_task(self, task, previous_result=None):
        task_number, function_name, *params, true_next_row, false_next_row = task
        function_to_call = getattr(self, function_name, None)
        
        if function_to_call and callable(function_to_call):
            print(f"Executing Task {task_number} with function: {function_name} and parameters: {', '.join(params)}")
            
            try:
                if 'additional_param' in function_to_call.__code__.co_varnames:
                    additional_param = previous_result if previous_result is not None else None
                    response = function_to_call(*params, additional_param=additional_param)
                else:
                    response = function_to_call(*params)

                print(f"Response from {function_name}: {response}")

                if isinstance(response, tuple) and len(response) > 1:
                    return (true_next_row, response[1]) if response[0] else (false_next_row, response[1])
                return true_next_row if response else false_next_row 
            except Exception as e:
                print(f"Error executing {function_name}: {e}")
                return false_next_row
        print(f"Error: Function {function_name} not found or not callable.")
        return false_next_row 

    def execute_tasks(self, tasks, current_row, previous_result=None):
        if current_row >= len(tasks):
            print("Reached end of tasks.")
            return

        next_row = self.execute_task(tasks[current_row], previous_result)
        if next_row == 'exit':
            print("Exiting task execution.")
            return

        if isinstance(next_row, tuple): 
            next_row_index = int(next_row[0])
            next_result = next_row[1] if len(next_row) > 1 else None
            self.execute_tasks(tasks, next_row_index, previous_result=next_result)
        elif next_row:
            next_row_parts = next_row.split(",")
            next_row_index = int(next_row_parts[0])
            next_result = next_row_parts[1] if len(next_row_parts) > 1 else None
            self.execute_tasks(tasks, next_row_index, previous_result=next_result)

    def read_tasks_from_csv(self, file_path):
        tasks = []
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                tasks.append(row)
        return tasks

    def execute_tasks_from_csv(self, index=None):
        if index is None:
            tasks = self.read_tasks_from_csv('workflows/workflow.csv')
        else:
            tasks = self.read_tasks_from_csv(f'workflows/{index}.csv')
        print(self.filepath)
        self.execute_tasks(tasks, 0)
