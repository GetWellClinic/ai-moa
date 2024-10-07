"""
Full Workflow Test Module for AI-MOA

This module contains the implementation of a full workflow test for the AI-MOA (AI-powered Medical Office Assistant) project.
It includes classes and functions to simulate and test the entire document processing workflow, from PDF extraction to AI analysis and EMR updates.

Copyright © 2024 by Spring Health Corporation <office(at)springhealth.org>
Toronto, Ontario, Canada

This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software, documentation, and configuration files.
These programs, documentation, and configuration files are made available to you as open source in the hopes that your clinic or organization
may find it useful and improve your care to the public by reducing administrative burden for your staff and service providers.

NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.

LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.

NOTICE: We hope that you will consider contributing to our common source code repository so that others may benefit from your shared work.
However, if you distribute this code or serve this application to users in modified form, or as part of a derivative work,
you are required to make your modified or derivative work source code available under the same herein described license.
Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work source code can be acquired publicly
in its latest most up-to-date version, within one month.
"""

import csv
import json
import os
import time

import PyPDF2
import fitz
import guidance
import requests
import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from guidance import select


import io
from PIL import Image
import pytesseract
from src.config.config_manager import ConfigManager

class Workflow:
    """
    Represents a workflow for processing medical documents in the AI-MOA system.

    This class encapsulates the entire process of document analysis, from OCR to AI-powered classification and EMR updates.

    Attributes:
        config (ConfigManager): Configuration manager for the workflow.
        patient_name (str): Name of the patient associated with the document.
        fileType (str): Type of the document being processed.
        demographic_number (str): Demographic number of the patient.
        mrp (str): Most Responsible Provider number.
        provider_number (list): List of provider numbers associated with the document.
        logFile (str): Path to the log file.
        document_description (str): Description of the document.
        filepath (str): Path to the document file being processed.
        tesseracted_text (str): Extracted text from the document using OCR.
        mistral (guidance.models.OpenAI): OpenAI model for AI analysis.
        enable_ocr_gpu (bool): Flag to enable GPU for OCR processing.
        url (str): URL for the AI API.
        headers (dict): Headers for API requests.
        categories (list): List of document categories.
        categories_code (list): List of category codes.
    """

    def __init__(self, filepath):
        """
        Initialize the Workflow instance.

        Args:
            filepath (str): Path to the document file to be processed.
        """
        self.config = ConfigManager()
        self.config.clear_shared_state()
        self.patient_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.logFile = self.config.get('general.logging.filename', 'log_test.txt')
        self.document_description = ''
        self.filepath = filepath
        self.tesseracted_text = None
        self.mistral = guidance.models.OpenAI(self.config.get('general.ai_config.model', "gpt-3.5-turbo-instruct"))
        self.enable_ocr_gpu = self.config.get('general.enable_ocr_gpu', True)
        self.url = self.config.get('general.ai_config.url', "http://127.0.0.1:5000/v1/chat/completions")
        self.headers = {
            "Authorization": f"Bearer {self.config.get('general.ai_config.auth_token', 'qwerty')}",
            "Content-Type": "application/json"
        }
        self.categories = self.config.document_categories

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
        self.logger.debug("Inside find_category_index")
        if '.' in text:
            text = text.replace('.', '')
        for index, category in enumerate(self.categories_code):
            for word in text.split():
                if word.lower() == category.lower():
                    self.logger.debug(f"Category index found: {index}")
                    # set file type
                    self.fileType = category.lower()
                    self.execute_tasks_from_csv(index)
                    return True
        return False

    def has_ocr(self):
        return False

    def extract_text_from_pdf(self):
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
            logger.error(f"An error occurred: {e}")
            return False

    def extract_text_doctr(self):
        """
        Extract text from a PDF file using the DocTR OCR model.

        This method processes the PDF file specified in self.filepath, extracts text from each page,
        and stores the result in self.tesseracted_text. It also measures and logs the time taken for OCR.

        Returns:
            bool: True if text extraction was successful, False otherwise.
        """
        start_time = time.time()
        pdf_path = self.filepath
        self.logger.debug(f"Processing PDF: {pdf_path}")
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
                self.logger.debug(f"Processing page {page.page_idx}")
                for block in page.blocks:
                    self.logger.debug("Processing block")
                    for line in block.lines:
                        text += '\n'
                        for word in line.words:
                            text += word.value + ' '

            self.tesseracted_text = text
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.append_to_file("Time taken for the OCR:")
            self.append_to_file(str(elapsed_time))
            self.mistral += text
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
        """
        Build and execute an AI prompt to classify the document.

        This method uses the Mistral AI model to classify the document based on the given prompt.
        It attempts the classification multiple times in case of failures.

        Args:
            prompt (str): The prompt to be used for document classification.

        Returns:
            bool: True if the prompt was successfully executed and a classification was obtained,
                  False if all attempts failed.
        """
        start_time = time.time()
        max_attempts = 5
        attempts = 0
        while attempts < max_attempts:
            try:
                with guidance.user():
                    lm = self.mistral + prompt
                with guidance.assistant():
                    lm += select(self.categories, name='ans')
                end_time = time.time()
                elapsed_time = end_time - start_time
                self.append_to_file("Time taken for the prompt:")
                self.append_to_file(str(elapsed_time))
                self.append_to_file("Document Type: " + lm["ans"])
                return True
            except guidance.models._model.ConstraintException as e:
                attempts += 1
                self.append_to_file(f"Attempt {attempts} failed. Retrying...")
        else:
            return False

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
                    "content": self.tesseracted_text + '. ' + prompt
                }
            ],
            "mode": "instruct",
            "temperature": .1,
            "character": "Assistant",
            "top_p": .1
            # max_tokens:100
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
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        if '.' in name:
            name = name.replace('.', '')
        self.append_to_file("Connecting to OSCAR to identify patient using patient name.")
        self.append_to_file("Test Mode, skipping api call to oscar.")
        self.logger.debug(f"Patient name: {name}")

    def set_doctor_from_code(self, name):
        oscar_response = []
        if name:
            if '.' in name:
                name = name.replace('.', '')

    def get_doctor_name(self, prompt):
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.logger.debug("Getting doctor name")
        self.logger.debug(f"Doctor name: {name}")
        array_pattern = r'\[.*?\]'
        oscar_response = []
        if name:
            if '.' in name:
                name = name.replace('.', '')

    def get_document_description(self, prompt):
        result = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.document_description = result
        return True

    def filter_results(self, prompt, additional_param=None):
        self.append_to_file("Filtering results: ")
        if additional_param is not None:
            details = self.build_sub_prompt(self.tesseracted_text + prompt + str(additional_param))
            self.logger.debug(f"Filtered results: {details}")
            return True, details
        else:
            self.append_to_file("Skipping filtering, not connected to oscar.")
            return False

    def set_patient(self, additional_param=None):
        self.append_to_file("Storing patient details. ")
        if additional_param is not None:
            self.logger.debug(f"Additional param: {additional_param}")
            data = json.loads(additional_param)
            self.patient_name = data[0]['formattedName'] + '(' + data[0]['fomattedDob'] + ')'
            self.demographic_number = data[0]['demographicNo']
            # Add MRP
            if data[0]['providerNo'] is not None:
                self.mrp = data[0]['providerNo']
            return True
        else:
            self.append_to_file("Skipping in test mode. ")
            return False

    def set_doctor(self, additional_param=None):
        self.append_to_file("Storing provider details. ")
        if additional_param is not None:
            # additional_param = '[{"firstName": "Michelle", "lastName": "Liu", "ohipNo": "", "providerNo": "999998"},{"firstName": "John", "lastName": "Doe", "ohipNo": "", "providerNo": "999998"}]'
            self.logger.debug(f"Additional param: {additional_param}")
            data = json.loads(additional_param)
            self.logger.debug(f"Provider data: {data}")
            for item in data:
                self.logger.debug(f"Processing item: {item}")
                if isinstance(item, dict):
                    if 'providerNo' in item:
                        self.logger.debug(f"Provider number: {item['providerNo']}")
                        self.provider_number.append(item['providerNo'])
            self.logger.debug(f"Provider numbers: {self.provider_number}")
            return True
        else:
            self.append_to_file("Skipping in test mode. ")
            return False

    def oscar_update(self):
        self.append_to_file("Updating details in OSCAR. ")
        self.append_to_file("Skipping OSCAR update in test mode. ")
        self.logger.debug(
            f"Document Details: Patient: {self.patient_name}, Demographic: {self.demographic_number}, Providers: {self.provider_number}, Type: {self.fileType}, Description: {self.document_description}")
        return True

    def execute_task(self, task, previous_result=None):
        task_number, function_name, *params, true_next_row, false_next_row = task
        function_to_call = getattr(self, function_name, None)

        if function_to_call and callable(function_to_call):
            print(f"Executing Task {task_number} with function {function_name} and parameters: {', '.join(params)}")

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
        if current_row >= len(tasks):
            print("Reached end of tasks.")
            return

        next_row = self.execute_task(tasks[current_row], previous_result)
        if next_row == 'exit':
            print("Exiting task execution.")
            return

        if isinstance(next_row, tuple):
            # print(next_row)
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
            tasks = self.read_tasks_from_csv(str(index) + '.csv')
        self.logger.debug(f"Processing file: {self.filepath}")
        self.execute_tasks(tasks, 0)

    def append_to_file(self, content):
        print(content)
        with open(self.logFile, "a") as file:
            file.write(content + "\n")


def get_pdf_files(folder_path):
    pdf_files = []
    files_to_remove = {
        "Sample-C10-002.pdf"
    }
    retrying_files = {

    }
    files_to_remove.update(retrying_files)
    for file in os.listdir(folder_path):
        if file.endswith(".pdf") and file not in files_to_remove:
            pdf_files.append(file)
    return pdf_files
    # return ["Sample-C3-003.pdf"]


if __name__ == "__main__":
    config = ConfigManager()
    folder_path = config.get('testing.full_workflow.folder_path', "/home/justinjoseph/Documents/AI-MOA/all_files/")
    # print(folder_path)
    pdf_files = get_pdf_files(folder_path)
    for pdf_file in pdf_files:
        start_time = time.time()
        workflow = Workflow(folder_path + pdf_file)
        workflow.append_to_file("File: " + pdf_file)
        workflow.execute_tasks_from_csv()
        end_time = time.time()
        elapsed_time = end_time - start_time
        workflow.append_to_file("Time taken for the file " + pdf_file + " : ")
        workflow.append_to_file(str(elapsed_time))
        # break
