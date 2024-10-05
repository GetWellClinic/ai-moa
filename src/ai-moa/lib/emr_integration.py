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
import datetime
import itertools
import json
import logging
import os
import re
import time
from typing import List, Dict, Any, Optional

import PyPDF2
import fitz
import requests
import torch
from bs4 import BeautifulSoup
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from src.utils.logging_config import setup_logging

logger = setup_logging()


class Workflow:
    def __init__(self, filepath: str, session: requests.Session, base_url: str, file_name: str, enable_ocr_gpu: bool):
        self.patient_name: str = ''
        self.fl_name: str = ''
        self.file_type: str = ''
        self.demographic_number: str = ''
        self.mrp: str = ''
        self.provider_number: List[int] = []
        self.document_description: str = ''
        self.filepath: str = filepath
        self.tesseracted_text: Optional[str] = None
        self.session: requests.Session = session
        self.base_url: str = base_url
        self.file_name: str = file_name
        self.enable_ocr_gpu: bool = enable_ocr_gpu
        self.url: str = "http://127.0.0.1:5000/v1/chat/completions"
        self.headers: Dict[str, str] = {
            "Authorization": "Bearer qwerty",
            "Content-Type": "application/json"
        }
        self.categories: List[str] = [
            "Lab", "Consult", "Insurance", "Legal", "Old Chart", "Radiology",
            "Pathology", "Others", "Photo", "Consent", "Diagnostics",
            "Pharmacy", "Requisition", "Referral", "Request"
        ]
        self.categories_code: List[str] = [
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

    # This method is not used and relies on pytesseract which is not imported
    # If needed in the future, uncomment and add necessary imports
    """
    def extract_text_from_pdf(self):
        # Implementation removed
        pass
    """

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
                for page_num in range(num_pages):  # Iterate over all pages
                    page = reader.pages[page_num]
                    text += page.extract_text()
            self.tesseracted_text = text
            # self.tesseracted_text = """"""
            return True
        except Exception as e:
            print("An error occurred:", e)
            return False

    def build_prompt(self, prompt):
        start_time = time.time()
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": f"Today's Date is: {datetime.datetime.now().date()}\n{self.tesseracted_text}\n. For the following question, from the list, choose all types that have at least one element in the EMR document, only if the element comprises more than 30% of the EMR document. If this is more than three types and the percentage is more than 30%, identify it always as 'Others'. Here are your options: Lab, Consult, Insurance, Legal, Old Chart, Radiology, Photo, Consent, Pathology, Diagnostics, Pharmacy, Requisition, HCC Referrals, Request. See descriptions of these terms below; these descriptions should be only used to help you to identify the correct term, and not to be used to display in the output.{prompt}\nBased on the document identified elements along with their percentages for the document."
                }
            ],
            "mode": "instruct",
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        content_value = response.json()['choices'][0]['message']['content']
        logger.info("First AI response received")
        logger.debug(f"First AI response: {content_value}")

        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": f"EMR Document content:{content_value}\nFor the following, only respond with one word and no explanations: From the provided information, identify the type of the EMR document based solely on the highest percentage given. If no percentage is available for any document type or if percentages are available but the type is not in the given list (Lab, Consult, Insurance, Legal, Old Chart, Radiology, Photo, Consent, Pathology, Diagnostics, Pharmacy, Requisition, HCC Referrals, Request), respond with 'Others'. If the top two types (based on highest percentages) have percentages that are very close to each other (within 5%) or the same percentage, select 'Others'. Additionally, if the top two types are Lab and Consult, Consult and Diagnostics, or Lab and Pathology, and if the percentage of the highest type among these pairs is not above 80%, identify it as 'Others'. Based on this, the type of the EMR document in one word will be ..."
                }
            ],
            "mode": "chat",
            "temperature": 0.1,
            "character": "Assistant",
            "top_p": 0.1
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        content_value = response.json()['choices'][0]['message']['content']
        logger.info("Second AI response received")
        logger.info(f"Document Type: {content_value}")

        self.find_category_index(content_value)

        end_time = time.time()
        logger.info(f"Total time for build_prompt: {end_time - start_time:.2f} seconds")
        return True

    def build_sub_prompt(self, prompt):
        start_time = time.time()
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
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.append_to_file("Response:")
        self.append_to_file(response.json()['choices'][0]['message']['content'])
        self.append_to_file("Time taken for the prompt:")
        self.append_to_file(str(elapsed_time))
        return response.json()['choices'][0]['message']['content']

    def get_patient_name(self, prompt):
        name = self.build_sub_prompt(f"{self.tesseracted_text}{prompt}")
        if '.' in name:
            name = name.replace('.', '')
        url = f"{self.base_url}/demographic/SearchDemographic.do"
        payload = {
            "query": f"%{name}%"
        }
        response = self.session.post(url, data=payload)
        response_data = json.loads(response.text)
        if not response_data["results"]:
            return False
        return True, response_data["results"]

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

    def getPatientHTML(self, type_of_query, query):
        url = f"{self.base_url}/demographic/demographiccontrol.jsp"
        payload = {
            "search_mode": type_of_query,
            "keyword": f"%{query}%",
            "orderby": ["last_name", "first_name"],
            "dboperation": "search_titlename",
            "limit1": 0,
            "limit2": 10,
            "displaymode": "Search",
            "ptstatus": "active",
            "fromMessenger": "False",
            "outofdomain": ""
        }
        response = self.session.post(url, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all(class_="odd") + soup.find_all(class_="even")
        return table

    def unidentified_patient(self, prompt):
        query = self.build_sub_prompt(f"{self.tesseracted_text}{prompt}")
        self.patient_name = "CONFIDENTIAL, UNATTACHED (2016-10-17)"
        self.demographic_number = "285"
        self.mrp = ""
        self.document_description = f"{query} {self.document_description}"
        return True

    def set_doctor_from_code(self, name):
        if name:
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
        oscar_response = []
        if name:
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
        self.document_description = result
        return True

    def filter_results(self, prompt, additional_param=None):
        self.append_to_file("Filtering results: ")
        if additional_param is not None:
            details = self.build_sub_prompt(f"{self.tesseracted_text}{prompt}{additional_param}")
            cleaned_string = details.replace("[", "").replace("]", "")
            return True, cleaned_string
        self.append_to_file("Skipping filtering, not connected to oscar.")
        return False

    def set_patient(self, additional_param=None):
        self.append_to_file("Storing patient details. ")
        if additional_param is not None:
            match = re.search(r'```json\n(.*?)```', additional_param, re.DOTALL)
            if match:
                additional_param = match.group(1)
            additional_param = additional_param.replace("'", '"')
            try:
                data = json.loads(additional_param)
                self.patient_name = f"{data['formattedName']}({data['formattedDob']})"
                self.fl_name = data['formattedName']
                self.demographic_number = data['demographicNo']
                if data['providerNo'] is not None:
                    self.mrp = data['providerNo']
                return True
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                return False
        self.append_to_file("Skipping in test mode. ")
        return False

    def set_doctor(self, additional_param=None):
        self.append_to_file("Storing provider details. ")
        if additional_param is not None:
            data = json.loads(additional_param)
            print(data)
            for item in data:
                if isinstance(item, dict) and 'providerNo' in item:
                    print(item['providerNo'])
                    self.provider_number.append(item['providerNo'])
            print(self.provider_number)
            return True
        self.append_to_file("Skipping in test mode. ")
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
            print(f"File not found: {e}")
        except IOError as e:
            print(f"Error reading the file: {e}")
        return data

    def getProviderListFromOscarLLMMode(self):
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
        response = self.session.post(url, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'tblResults'})

        if table:
            data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant designed to output JSON."
                    },
                    {
                        "role": "user",
                        "content": f"From the below html content list the lastname, firstname and provider number for all the providers and return the list as a json array. Only return the json array nothing else.{table}"
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
            return content_value
        return None

    def oscar_update(self):
        print("Document Details:")
        print(self.patient_name)
        print(self.demographic_number)
        print(self.provider_number)
        print(self.document_description)
        url = f"{self.base_url}/dms/ManageDocument.do"

        params = {
            "method": "documentUpdateAjax",
            "documentId": self.file_name,
            "docType": self.file_type,
            "documentDescription": self.document_description,
            "observationDate": str(datetime.datetime.now().date()),
            "demog": self.demographic_number,
            "demofindName": self.fl_name,
            "demoName": self.fl_name,
            "demographicKeyword": self.patient_name
        }

        params["flagproviders"] = []

        # Add provider to all
        self.provider_number.append(127)
        params["flagproviders"] = self.provider_number.copy()
        response = self.session.post(url, data=params)
        return True

    def execute_task(self, task, previous_result=None):
        task_number, function_name, *params, true_next_row, false_next_row = task
        function_to_call = getattr(self, function_name, None)

        if function_to_call and callable(function_to_call):
            logger.info(
                f"Executing Task {task_number} with function {function_name} and parameters: {', '.join(params)}")

            try:
                if 'additional_param' in function_to_call.__code__.co_varnames:
                    additional_param = previous_result if previous_result is not None else None
                    response = function_to_call(*params, additional_param=additional_param)
                else:
                    response = function_to_call(*params)

                logger.info(f"Response from {function_name}: {response}")

                if isinstance(response, tuple) and len(response) > 1:
                    return (true_next_row, response[1]) if response[0] else (false_next_row, response[1])
                return true_next_row if response else false_next_row
            except Exception as e:
                logger.error(f"Error executing {function_name}: {e}")
                return false_next_row
        logger.error(f"Error: Function {function_name} not found or not callable.")
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
            tasks = list(reader)
        return tasks

    def execute_tasks_from_csv(self, index=None):
        file_path = 'workflows/workflow.csv' if index is None else f'workflows/{index}.csv'
        tasks = self.read_tasks_from_csv(file_path)
        print(self.filepath)
        self.execute_tasks(tasks, 0)

    def append_to_file(self, content):
        print(content)
        with open(self.log_file, "a") as file:
            file.write(f"{content}\n")


def get_pdf_files(folder_path):
    files_to_remove = set()
    retrying_files = set()
    files_to_remove.update(retrying_files)
    pdf_files = [file for file in os.listdir(folder_path) if file.endswith(".pdf") and file not in files_to_remove]
    return sorted(pdf_files)
