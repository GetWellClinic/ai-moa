import csv
import re
import random
import torch
import fitz
import PyPDF2
import requests
import json
import datetime
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from bs4 import BeautifulSoup

class Workflow:
    def __init__(self, filepath, session, base_url, file_name, enable_ocr_gpu):
        self.patient_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.document_description = ''
        self.filepath = filepath
        self.tesseracted_text = None
        self.session = session
        self.base_url = base_url
        self.file_name = file_name
        self.enable_ocr_gpu = enable_ocr_gpu
        self.url = "http://127.0.0.1:5000/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer qwerty",
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

    def find_category_index(self, text):
        if '.' in text:
            text = text.replace('.', '')
        for index, category in enumerate(self.categories_code):
            for word in text.split():
                if word.lower() == category.lower():
                    print(index)
                    self.fileType = category.lower()
                    self.execute_tasks_from_csv(index)
                    return True
        return False

    def has_ocr(self):
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
            print("An error occurred:", e)
            return False

    def extract_text_doctr(self):
        pdf_path = self.filepath
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
            print("An error occurred:", e)
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
            print("An error occurred:", e)
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
                    "content": self.tesseracted_text + '. ' + prompt
                }
            ],
            "mode": "instruct",
            "temperature": .1,
            "character": "Assistant",
            "top_p": .1
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
            "temperature": .1,
            "character": "Assistant",
            "top_p": .1
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()['choices'][0]['message']['content']

    def get_patient_name(self, prompt):
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        if '.' in name:
            name = name.replace('.', '')
        print(name)
        url = f"{self.base_url}/demographic/SearchDemographic.do"
        payload = {
            "query": name
        }
        response = self.session.post(url, data=payload)
        response_data = json.loads(response.text)
        if len(response_data["results"]) == 0:
            return False
        else:
            return True, response_data["results"]

    def set_doctor_from_code(self, name):
        oscar_response = []
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
                if isinstance(item, dict):
                    if 'providerNo' in item:
                        self.provider_number.append(item['providerNo'])
            if self.provider_number is not None:
                return True
            else:
                return False

    def get_doctor_name(self, prompt):
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
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
            if len(response_data["results"]) != 0:
                results = response_data["results"]
                if isinstance(results, list):
                    for item in results:
                        if isinstance(item, dict):
                            oscar_response.append(item)
            if len(oscar_response) != 0:
                return True, oscar_response
            else:
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
        query = self.build_sub_prompt(self.tesseracted_text + prompt)
        if query:
            if '.' in query:
                query = query.replace('.', '')
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
            response = self.session.post(url, data=payload)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find_all(class_="odd")
            table += soup.find_all(class_="even")
            if table:
                print(str(table))
                return True, str(table)
            else:
                return False

    def getProviderList(self, prompt):
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
            oscar_response = self.build_sub_prompt(prompt + str(table))
            return True, oscar_response
        else:
            return False

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
            "docType": self.fileType,
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
        params["flagproviders"] = []
        for value in self.provider_number:
            params["flagproviders"].append(value)
        response = self.session.post(url, data=params)
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
                else:
                    return true_next_row if response else false_next_row 
            except Exception as e:
                print(f"Error executing {function_name}: {e}")
                return false_next_row
        else:
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
        else:
            next_row_parts = next_row.split(",") if next_row else None
            if next_row_parts:
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
            tasks = self.read_tasks_from_csv('workflow.csv')
        else:
            tasks = self.read_tasks_from_csv(str(index)+'.csv')
        print(self.filepath)
        self.execute_tasks(tasks, 0)
