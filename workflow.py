import csv
import re
import random
import fitz
import PyPDF2
import requests
import json
import datetime
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

class Workflow:
    def __init__(self, filepath, session, base_url, file_name):
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
        self.url = "http://127.0.0.1:5000/v1/chat/completions"
        # the Authorization qwerty will have to be changed, this for testing
        self.headers = {
            "Authorization": "Bearer qwerty",
            "Content-Type": "application/json"
        }
        self.categories = [
                            "Lab",
                            "Consult",
                            "Insurance",
                            "Legal",
                            "Old Chart",
                            "Radiology",
                            "Pathology",
                            "Others",
                            "Photo",
                            "Consent",
                            "Diagnostics",
                            "Pharmacy",
                            "Requisition",
                            "Referral",
                            "Request"
                        ]

        self.categories_code = [
                            "Lab",
                            "Consult",
                            "Insurance",
                            "Legal",
                            "OldChart",
                            "Radiology",
                            "Pathology",
                            "Others",
                            "Photo",
                            "Consent",
                            "Diagnostics",
                            "Pharmacy",
                            "Requisition",
                            "Referral",
                            "Request"
                        ]

    def find_category_index(self, text):
        """
        Finds the index of a category in the text and sets the fileType attribute.
        Calls execute_tasks_from_csv with the index if a category is found.

        :param text: Text to search for categories.
        :return: True if category found, else False.
        """
        print("inside find_category_index")
        if '.' in text:
            text = text.replace('.', '')
        for index, category in enumerate(self.categories_code):
            for word in text.split():
                if word.lower() == category.lower():
                    print(index)
                    # set file type
                    self.fileType = category.lower()
                    self.execute_tasks_from_csv(index)
                    return True
        return False

    def has_ocr(self):
        """
        Checks if the PDF file has OCR text.

        :return: True if OCR text is found, else False.
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
            print("An error occurred:", e)
            return False

    def extract_text_from_pdf(self):
        """
        Extracts text from images within the PDF using Tesseract OCR.

        :return: True if text extraction is successful, else False.
        """
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
            print("An error occurred:", e)
            return False

    def extract_text_doctr(self):
        """
        Extracts text from PDF using the Doctr OCR model.

        :return: True if text extraction is successful, else False.
        """
        pdf_path = self.filepath
        print(pdf_path)
        text = ''
        try:
            model = ocr_predictor(pretrained=True)

            # PDF
            doc = DocumentFile.from_pdf(pdf_path)

            # Analyze
            result = model(doc)
            # Iterate through pages
            for page in result.pages:
                # Iterate through blocks
                for block in page.blocks:
                    # Iterate through lines
                    for line in block.lines:
                        text += '\n'
                        # Print words in the line
                        for word in line.words:
                            text += word.value + ' '

            self.tesseracted_text = text
            return True
        except Exception as e:
            print("An error occurred:", e)
            return False

    def extract_text_from_pdf_file(self):
        """
        Extracts text from PDF using PyPDF2.

        :return: True if text extraction is successful, else False.
        """
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
            print("An error occurred:", e)
            return False

    def build_prompt(self, prompt):
        """
        Builds a prompt for the external service and processes the response.

        :param prompt: Additional prompt text.
        :return: True if successful.
        """
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
        """
        Builds a sub-prompt for the external service and returns the response content.

        :param prompt: Additional prompt text.
        :return: Response content from the external service.
        """
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
        return response.json()['choices'][0]['message']['content']

    def get_patient_name(self, prompt):
        """
        Retrieves the patient name using the provided prompt.

        :param prompt: Prompt text to use.
        :return: True and patient results if successful, else False.
        """
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        if '.' in name:
            name = name.replace('.', '')
        print(name)
        url = f"{self.base_url}/demographic/SearchDemographic.do"

        # Define the payload data
        payload = {
            "query": name
        }

        # Send the POST request
        response = self.session.post(url, data=payload)

        response_data = json.loads(response.text)

        if len(response_data["results"]) == 0:
            return False
        else:
            return True, response_data["results"]

    def set_doctor_from_code(self, name):
        """
        Sets the doctor from the code provided.

        :param name: Doctor's name or code.
        :return: True if provider number is found, else False.
        """
        oscar_response = []
        if name:
            if '.' in name:
                name = name.replace('.', '')

            url = f"{self.base_url}/provider/SearchProvider.do"

            # Define the payload data
            payload = {
                "query": name
            }

            # Send the POST request
            response = self.session.post(url, data=payload)
            data = json.loads(response.text)

            for item in data["results"]:
                if isinstance(item, dict) and 'providerNo' in item:
                    self.provider_number.append(item['providerNo'])

            return bool(self.provider_number)

    def get_doctor_name(self, prompt):
        """
        Retrieves the doctor name using the provided prompt.

        :param prompt: Prompt text to use.
        :return: True and doctor results if successful, else False.
        """
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

            # Send the POST request
            response = self.session.post(url, data=payload)
            response_data = json.loads(response.text)

            if response_data["results"]:
                for item in response_data["results"]:
                    if isinstance(item, dict):
                        oscar_response.append(item)

            return bool(oscar_response), oscar_response

    def get_document_description(self, prompt):
        """
        Retrieves the document description using the provided prompt.

        :param prompt: Prompt text to use.
        :return: True if successful.
        """
        result = self.build_sub_prompt(self.tesseracted_text + prompt)
        print(result)
        self.document_description = result
        return True

    def filter_results(self, prompt, additional_param=None):
        """
        Filters results based on the provided prompt and additional parameters.

        :param prompt: Prompt text to use.
        :param additional_param: Additional parameters to use for filtering.
        :return: True and details if additional_param is provided, else False.
        """
        if additional_param:
            details = self.build_sub_prompt(self.tesseracted_text + prompt + str(additional_param))
            return True, details
        return False

    def set_patient(self, additional_param=None):
        """
        Sets the patient details from the additional parameters.

        :param additional_param: Additional parameters to use.
        :return: True if successful, else False.
        """
        if additional_param:
            data = json.loads(additional_param)
            self.patient_name = data[0]['formattedName'] + '(' + data[0]['fomattedDob'] + ')'
            self.demographic_number = data[0]['demographicNo']
            if data[0]['providerNo']:
                self.mrp = data[0]['providerNo']
            return True
        return False

    def set_doctor(self, additional_param=None):
        """
        Sets the doctor details from the additional parameters.

        :param additional_param: Additional parameters to use.
        :return: True if successful, else False.
        """
        if additional_param:
            data = json.loads(additional_param)
            print(data)
            for item in data:
                if isinstance(item, dict) and 'providerNo' in item:
                    print(item['providerNo'])
                    self.provider_number.append(item['providerNo'])
            print(self.provider_number)
            return True
        return False

    def oscar_update(self):
        """
        Updates the Oscar system with the document details.

        :return: True if successful.
        """
        url = f"{self.base_url}/dms/ManageDocument.do"

        # Define the parameters
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

        params["flagproviders"] = self.provider_number

        print(params)

        response = self.session.post(url, data=params)

        print(response)

        return True

    def execute_task(self, task, previous_result=None):
        """
        Executes a single task from the task list.

        :param task: Task to execute.
        :param previous_result: Result from the previous task.
        :return: Next task index and result, or exit if function not found or not callable.
        """
        task_number, function_name, *params, true_next_row, false_next_row = task
        function_to_call = getattr(self, function_name, None)
        
        if function_to_call and callable(function_to_call):
            print(f"Executing Task {task_number} with function: {function_name} and parameters: {', '.join(params)}")
            
            if 'additional_param' in function_to_call.__code__.co_varnames:
                additional_param = previous_result if previous_result is not None else None
                response = function_to_call(*params, additional_param=additional_param)
            else:
                response = function_to_call(*params)

            print(f"Response from {function_name}: {response}")

            if isinstance(response, tuple) and len(response) > 1:
                if response[0]:
                    return true_next_row, response[1]
                else:
                    return false_next_row, response[1]
            else:
                return true_next_row if response else false_next_row 
        else:
            print(f"Error: Function {function_name} not found or not callable.")
            return false_next_row 

    def execute_tasks(self, tasks, current_row, previous_result=None):
        """
        Executes tasks recursively starting from the current row.

        :param tasks: List of tasks to execute.
        :param current_row: Index of the current task.
        :param previous_result: Result from the previous task.
        """
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
        """
        Reads tasks from a CSV file.

        :param file_path: Path to the CSV file.
        :return: List of tasks.
        """
        tasks = []
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                tasks.append(row)
        return tasks

    def execute_tasks_from_csv(self, index=None):
        """
        Executes tasks read from a CSV file.

        :param index: Index of the CSV file to read from. Default is None.
        """
        if index is None:
            tasks = self.read_tasks_from_csv('./workflow-config/workflow.csv')
        else:
            tasks = self.read_tasks_from_csv('./workflow-config/' + str(index) + '.csv')
        print(self.filepath)
        self.execute_tasks(tasks, 0)
