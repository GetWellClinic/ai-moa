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

import os
import csv
import re
import random
import itertools
import torch
import fitz
import PyPDF2
import requests
import json
import datetime
import time
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from bs4 import BeautifulSoup

import logging

class Workflow:
    def __init__(self, filepath, session, base_url, file_name, enable_ocr_gpu, config):
        self.patient_name = ''
        self.fl_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.config = config
        self.logFile = self.config.get('logging', {}).get('filename', "log_test_28_emr_test.txt")
        self.document_description = ''
        self.filepath = filepath
        self.tesseracted_text = None
        self.session = session
        self.base_url = base_url
        self.file_name = file_name
        self.enable_ocr_gpu = enable_ocr_gpu
        self.logger = logging.getLogger(__name__)
        self.url = self.config.get('ai_config', {}).get('url', "http://127.0.0.1:5000/v1/chat/completions")
        self.headers = {
            "Authorization": f"Bearer {self.config.get('ai_config', {}).get('auth_token', 'qwerty')}",
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
                            "Request",
                            "Advertisement"
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
                            "Request",
                            "Advertisement"
                        ]

    def find_category_index(self,text):
        self.logger.debug("Inside find_category_index")
        if '.' in text:
            text = text.replace('.', '')
        for word in text.split():
            for index, category in enumerate(self.categories_code):
                if '"' in word:
                    word = word.replace('"', '')
                if "'" in word:
                    word = word.replace("'", "")
                if word.lower() == category.lower():
                    self.logger.debug(f"Category index found: {index}")
                    #set file type
                    self.fileType = category.lower()
                    self.execute_tasks_from_csv(index)
                    return True
        self.fileType = 'others'
        self.execute_tasks_from_csv(7)

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
            self.logger.error(f"An error occurred: {e}")
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
            self.logger.error(f"An error occurred: {e}")
            return False

    def extract_text_doctr(self):
        start_time = time.time()
        pdf_path = self.filepath
        self.logger.debug("Processing PDF: %s", pdf_path)
        self.logger.debug("Processing PDF: %s", pdf_path)
        text = ''
        try:
            if(self.enable_ocr_gpu == True):
                device = torch.device("cuda:0")
                model = ocr_predictor(pretrained=True).to(device)
            else:
                model = ocr_predictor(pretrained=True)
            # PDF
            doc = DocumentFile.from_pdf(pdf_path)

            # Analyze
            result = model(doc)
            # Iterate through pages
            for page in result.pages:
                self.logger.debug("Processing page %d", page.page_idx)
                
                # Iterate through blocks
                for block in page.blocks:
                    self.logger.debug("Processing block")
                    
                    # Iterate through lines
                    for line in block.lines:
                        text += '\n'
                        
                        # Print words in the line
                        for word in line.words:
                            text += word.value + ' '

            self.tesseracted_text = text
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.append_to_file("Time taken for the OCR:")
            self.append_to_file(str(elapsed_time))
            return True
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
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
            #self.tesseracted_text = """"""
            return True
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return False

    def build_prompt(self,prompt):
        start_time = time.time()
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": "Today's Date is : "+str(datetime.datetime.now().date())+'\n'+ self.tesseracted_text + '\n. '+"""

                    Act as a helpful medical office assistant to perform the following instructions to identify the correct document category type for documents that you review.
                     Infer the confidence level in percentage for each document category in the CATEGORY LIST based on the definitions in the DOCUMENT DEFINITIONS.
                     This is very Important: If the documents do not have any information related to patient always give highest priority to the category type 'Advertisement'.
                      For your reference, these are the CATEGORY LIST: lab, consult, insurance, legal, oldchart, radiology, photo, consent, diagnostics, pharmacy, requisition, referral, request, advertisement, miscellaneous.
                      For your reference, these are the DOCUMENT DEFINITIONS: """+ prompt + """"
                        Based on this, identify all the document categories that has elements from the 'CATEGORY LIST' with their confidence levels in percentage sorted in descending order without any explanation.

                        Determine the document category with the highest confidence level percentage for the EMR document using the following rules:

                            Step a. If the confidence level percentage is more than 60% for the category type 'Advertisement', then
                               the category type is 'Advertisement'. If the confidence level percentage is less than 60% for the category type 'Advertisement', then
                               go to next step. 

                            Step b. If there is only one category to select from, select that category as the document category.
                                If there is more that one category to select from go to next step.

                            Step c. Identify the top two document categories based on their confidence level percentage.
                            
                            Step d. If the top two categories are "Requisition" and "Radiology," and both have confidence levels below 60%, select "Miscellaneous" as the document category. Else go to next step.

                            Step e. If the confidence level difference between the top two categories is less than 10%, select "Miscellaneous" as the document category. Else go to next step.
                            
                            Step f. If neither of the above conditions apply, select the top document category with the highest confidence level percentage.

                          """
                }
            ],
            "mode": "instruct",
            "temperature": self.config.get('ai_config', {}).get('temperature', 0.1),
            "character": "Assistant",
            "top_p": self.config.get('ai_config', {}).get('top_p', 0.1)
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        self.logger.debug("LLM response: %s", response.json())
        content_value = response.json()['choices'][0]['message']['content']
        self.logger.debug("Content value: %s", content_value)
        self.append_to_file("Response:")
        self.append_to_file(response.json()['choices'][0]['message']['content'])

        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": "EMR Document content:"+content_value + "\n" + """"                

                Based on this, the document category for the EMR document in one word will be ..."""
                
                }
            ],
            "mode": "chat",
            "temperature": self.config.get('ai_config', {}).get('temperature', 0.1),
            "character": "Assistant",
            "top_p": self.config.get('ai_config', {}).get('top_p', 0.1)
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        self.logger.debug("LLM response: %s", response.json())
        content_value = response.json()['choices'][0]['message']['content']
        self.logger.debug("Content value: %s", content_value)
        self.append_to_file("Second Response:")
        self.append_to_file(response.json()['choices'][0]['message']['content'])
        self.append_to_file("Second Document Type: "+content_value)

        self.find_category_index(content_value)

        return True

    def build_sub_prompt(self,prompt):
        start_time = time.time()
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user",
                    "content": self.tesseracted_text + '. '+ prompt
                }
            ],
            "mode": "instruct",
            "temperature": .1,
            "character": "Assistant",
            "top_p":.1
            #max_tokens:100
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.append_to_file("Response:")
        self.append_to_file(response.json()['choices'][0]['message']['content'])
        self.append_to_file("Time taken for the prompt:")
        self.append_to_file(str(elapsed_time))
        return response.json()['choices'][0]['message']['content']

    def get_patient_name(self,prompt):
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        if '.' in name:
            name = name.replace('.', '')
        self.logger.debug("Patient name: %s", name)
        url = f"{self.base_url}/demographic/SearchDemographic.do"

        payload = {
            "query": "%"+name+"%"
        }

        response = self.session.post(url, data=payload)

        self.logger.debug("Response text: %s", response.text)

        response_data = json.loads(response.text)

        if len(response_data["results"]) == 0:
            return False
        else:
            return True,response_data["results"]

    def patientSearch(self,prompt,type_of_query):
        # to be used to search for a demographic using the below types
        # Type : search_name,search_phone,search_dob,search_address,search_hin,search_chart_no,search_demographic_no
        # filter_results can be used to select one from that array
        query = self.build_sub_prompt(self.tesseracted_text + prompt)
        # query = "OO7"
        if "False" in query:
            return False
        array_pattern = r'\[.*?\]'
        parts = query.split(':')
        parts = [part.strip() for part in parts]
        if len(parts) > 1:
            query = parts[1]

        if type_of_query == "search_dob":

            pattern = r'\bdate of birth of the patient\b.*?[.!?]'
            match = re.search(pattern, query)

            if match:
                query = match.group()
                # print(query)

            pattern = r'\d{4}-\d{2}-\d{2}'
            match = re.search(pattern, query)

            patternText = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b'
            matchText = re.search(patternText, query)

            if match:
                query = match.group()
                # print(query)
            elif matchText:
                query = matchText.group()
                query = self.convert_date(query)

        if type_of_query == "search_hin":
            pattern = r'\b\d{6,}[A-Za-z]*\b'
            match = re.search(pattern, query)
            if match:
                query = match.group()
                query = query[:-2]


        if type_of_query == "search_name":
            pattern = r'\bfull name of the patient\b.*?[.!?]'
            match = re.search(pattern, query)
            if match:
                query = match.group()

        if query:

            if '.' in query:
                query = query.replace('.', '')

            if ',' in query:
                query = query.replace(',', '')

            if type_of_query != "search_name":

                table = self.getPatientHTML(type_of_query,query)

                if table:
                    # print(str(table))
                    return True,str(table)
                else:
                    return False

            parts = query.split(' is ')
            if len(parts) > 1:
                name_parts = parts[1].split()
            else:
                name_parts = query.split()

            if len(name_parts) > 5:
                return False
            
            # print(name_parts)

            all_combinations = list(itertools.permutations(name_parts))
            formatted_combinations = [f"%{combo[0]}%,%{'%'.join(combo[1:])}%" for combo in all_combinations]

            for combo in formatted_combinations:
                # print(combo)
                table = self.getPatientHTML(type_of_query,combo)

                if table:
                    # print(str(table))
                    return True,str(table)

        return False

    def convert_date(self,query):
        # Split the string into components
        month_str, day_str, year_str = query.split()
        day = int(day_str[:-1])  # Remove the comma and convert to integer
        year = int(year_str)  # Convert year to integer

        # Create a mapping for month names to numbers
        months = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }

        # Get the month number from the mapping
        month = months[month_str]

        # Format the date as YYYY-MM-DD
        formatted_date = f"{year}-{month}-{day:02d}"
        
        return formatted_date


    def getPatientHTML(self,type_of_query,query):
        url = f"{self.base_url}/demographic/demographiccontrol.jsp"

        # Define the payload data
        payload = {
                      "search_mode": type_of_query,
                      "keyword": "%"+query+"%",
                      "orderby": ["last_name", "first_name"],
                      "dboperation": "search_titlename",
                      "limit1": 0,
                      "limit2": 10,
                      "displaymode": "Search",
                      "ptstatus": "active",
                      "fromMessenger": "False",
                      "outofdomain": ""
                    }

        # Send the POST request
        response = self.session.post(url, data=payload)

        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find_all(class_="odd")
        table += soup.find_all(class_="even")

        return table


    def unidentified_patient(self,prompt):
        query = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.patient_name = "CONFIDENTIAL, UNATTACHED (2016-10-17)"
        self.demographic_number = "285"
        self.mrp = ""
        self.document_description = query +" "+ self.document_description
        return True

    def set_doctor_from_code(self,name):
        self.logger.debug(f"Setting doctor from code: {name}")
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

            self.logger.debug("Provider search response: %s", response.text)

            self.logger.debug(f"Patient search response: {response.text}")

            data = json.loads(response.text)

            self.logger.debug("Provider data: %s", data)

            for item in data["results"]:
                self.logger.debug("Processing item: %s", item)
                if isinstance(item, dict):
                    if 'providerNo' in item:
                        self.logger.debug("Provider number: %s", item['providerNo'])
                        self.provider_number.append(item['providerNo'])

            self.logger.debug("Provider numbers: %s", self.provider_number)

            if self.provider_number is not None:
                return True
            else:
                return False

    def get_doctor_name(self,prompt):
        name = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.logger.debug("Getting doctor name")
        self.logger.debug("Doctor name: %s", name)
        array_pattern = r'\[.*?\]'
        #name = "Sokolowski"
        #array_match = re.search(array_pattern, names)
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

            self.logger.debug("Provider search response: %s", response.text)

            self.logger.debug(f"Patient search response: {response.text}")

            response_data = json.loads(response.text)

            if len(response_data["results"]) != 0:
                results = response_data["results"]
                if isinstance(results, list):
                    for item in results:
                        if isinstance(item, dict):
                            oscar_response.append(item)

            if len(oscar_response) != 0:
                return True,oscar_response
            else:
                return False

            self.logger.debug("Oscar response: %s", oscar_response)

    def get_document_description(self,prompt):
        result = self.build_sub_prompt(self.tesseracted_text + prompt)
        self.document_description = result
        return True

    def filter_results(self,prompt,additional_param=None):
        self.append_to_file("Filtering results: ")
        if additional_param is not None:
            details = self.build_sub_prompt(self.tesseracted_text + prompt + str(additional_param))
            cleaned_string = details.replace("[", "").replace("]", "")
            self.logger.debug("Filtered results: %s", details)
            return True,cleaned_string
        else:
            self.append_to_file("Skipping filtering, not connected to oscar.")
            return False

    def set_patient(self,additional_param=None):
        self.append_to_file("Storing patient details. ")
        if additional_param is not None:
            self.logger.debug("Additional param: %s", additional_param)
            match = re.search(r'```json\n(.*?)```', additional_param, re.DOTALL)

            if match:
                additional_param = match.group(1)
            
            additional_param = additional_param.replace("'", '"')

            try:
                data = json.loads(additional_param)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decoding error: {e}")
                return False

            self.patient_name = data['formattedName'] + '(' + data['formattedDob'] + ')'
            self.fl_name = data['formattedName']
            self.demographic_number = data['demographicNo']
            # Add MRP
            if data['providerNo'] is not None:
                self.mrp = data['providerNo']
            self.logger.info(f"Patient set: {self.patient_name}")
            return True
        else:
            self.append_to_file("Skipping in test mode. ")
            return False

    def set_doctor(self,additional_param=None):
        self.append_to_file("Storing provider details. ")
        if additional_param is not None:
            #additional_param = '[{"firstName": "Michelle", "lastName": "Liu", "ohipNo": "", "providerNo": "999998"},{"firstName": "John", "lastName": "Doe", "ohipNo": "", "providerNo": "999998"}]'
            self.logger.debug("Additional param: %s", additional_param)
            data = json.loads(additional_param)
            self.logger.debug("Provider data: %s", data)
            for item in data:
                self.logger.debug("Processing item: %s", item)
                if isinstance(item, dict):
                    if 'providerNo' in item:
                        self.logger.debug("Provider number: %s", item['providerNo'])
                        self.provider_number.append(item['providerNo'])
            #self.provider_number.append(data[0]['providerNo'])
            #self.provider_number.append(data[0]['providerNo'])
            #self.provider_number = data[0]['providerNo']
            self.logger.debug("Provider numbers: %s", self.provider_number)
            return True
        else:
            self.append_to_file("Skipping in test mode. ")
            return False

    def getProviderList(self,prompt):

            # content_value = self.getProviderListFromOscarLLMMode()
            # provider_list = json.dumps(content_value)

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
                        "content": self.tesseracted_text+ prompt + str(provider_list)
                    }
                ],
                "mode": "instruct",
                #should be a parameter, only if needed else default api values
                "temperature": .1,
                "character": "Assistant",
                #should be a parameter
                "top_p":.1
                #should be a parameter
                #max_tokens:100
            }
            response = requests.post(self.url, headers=self.headers, json=data)
            self.logger.debug("LLM response: %s", response.json())
            content_value = response.json()['choices'][0]['message']['content']

            self.logger.debug("Content value: %s", content_value)

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
        # Handle the case where the file is not found
            print(f"File not found: {e}")
        except IOError as e:
            # Handle other I/O errors (e.g., file read/write errors)
            print(f"Error reading the file: {e}")

        # print(data)

        return data


    def getProviderListFromOscarLLMMode(self):
        # to be used to get all the providers list from oscar.
        # filter_results should be used to select one from that array
        url = f"{self.base_url}/admin/providersearchresults.jsp"

        # Define the payload data
        payload = {
                      "search_mode": "search_providerno",
                      "search_status": "All",
                      "keyword": "",
                      "button": "",
                      "orderby": "last_name",
                      "limit1": 0,
                      "limit2": 10000
                    }

        # Send the POST request
        response = self.session.post(url, data=payload)

        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', {'id': 'tblResults'})

        if table:
            #print(table)
            # oscar_response = self.build_sub_prompt(self.tesseracted_text + prompt + str(table))
            self.logger.debug("Oscar response: %s", oscar_response)
            data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant designed to output JSON."
                    },
                    {
                        "role": "user",
                        "content": "From the below html content list the lastname, firstname and provider number for all the providers and return the list as a json array. Only return the json array nothing else."+ str(table)
                    }
                ],
                "mode": "instruct",
                #should be a parameter, only if needed else default api values
                "temperature": .1,
                "character": "Assistant",
                #should be a parameter
                "top_p":.1
                #should be a parameter
                #max_tokens:100
            }
            response = requests.post(self.url, headers=self.headers, json=data)
            self.logger.debug("LLM response: %s", response.json())
            content_value = response.json()['choices'][0]['message']['content']
            print(content_value)
            return content_value


    def oscar_update(self):
        self.logger.debug("Document Details: Patient: %s, Demographic: %s, Providers: %s, Type: %s, Description: %s", 
                          self.patient_name, self.demographic_number, self.provider_number, self.fileType, self.document_description)
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
            "save": "Save & Next"
        }

        params["flagproviders"] = []

        # Add provider to all
        self.provider_number.append(127)

        for value in self.provider_number:
            params["flagproviders"].append(value)

        self.logger.debug("Oscar update params: %s", params)

        response = self.session.post(url, data=params)

        self.logger.debug("Oscar update response status: %s", response.status_code)
        self.logger.debug("Oscar update response: %s", response.text)

        return True

    # More available funcitons and its usage

    # def ask_ai(self,param,additional_param=None):
    #     print(f"Executing ask_ai with parameter: {param}, additional_param={additional_param}")
    #     return random.choice([True, False]),"test"

    # def flag_email(self,param):
    #     print(f"Executing flag_email with parameter: {param}")
    #     return random.choice([True, False])

    # def get_patient_details(self,param1, param2,additional_param=None):
    #     print(f"Executing get_patient_details with parameters: {param1}, {param2}, additional_param={additional_param}")
    #     return random.choice([True, True]),"1245dsd"

    # def update_oscar(self,param1, param2, additional_param=None):
    #     print(f"Executing update_oscar with parameters: {param1}, {param2}, additional_param={additional_param}")
    #     return random.choice([True, True])


    def execute_task(self,task, previous_result=None):
        task_number, function_name, *params, true_next_row, false_next_row = task
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
                    return false_next_row,response[1]
            else:
                return true_next_row if response else false_next_row 
        else:
            self.logger.error(f"Error: Function {function_name} not found or not callable.")
            return false_next_row 

    def execute_tasks(self,tasks, current_row, previous_result=None):
        if current_row >= len(tasks):
            self.logger.info("Reached end of tasks.")
            return

        next_row = self.execute_task(tasks[current_row], previous_result)
        if next_row == 'exit':
            self.logger.info("Exiting task execution.")
            return

        if isinstance(next_row, tuple): 
            #print(next_row)
            next_row_index = int(next_row[0])
            next_result = next_row[1] if len(next_row) > 1 else None
            self.execute_tasks(tasks, next_row_index, previous_result=next_result)
        else:
            next_row_parts = next_row.split(",") if next_row else None
            if next_row_parts:
                next_row_index = int(next_row_parts[0])
                next_result = next_row_parts[1] if len(next_row_parts) > 1 else None
                self.execute_tasks(tasks, next_row_index, previous_result=next_result)


    def read_tasks_from_csv(self,file_path):
        tasks = []
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                tasks.append(row)
        return tasks

    def execute_tasks_from_csv(self,index=None):
        if index is None:
            tasks = self.read_tasks_from_csv('workflow.csv')
        else:
            tasks = self.read_tasks_from_csv(str(index)+'.csv')
        self.logger.debug("Processing file: %s", self.filepath)
        self.logger.debug(f"Processing file: {self.filepath}")
        self.execute_tasks(tasks, 0)

    def append_to_file(self,content):
        self.logger.debug(content)
        with open(self.logFile, "a") as file:
            file.write(content + "\n")

def get_pdf_files(folder_path):
    pdf_files = []
    files_to_remove = {

    }
    retrying_files = {
        
    }
    files_to_remove.update(retrying_files)
    for file in os.listdir(folder_path):
        if file.endswith(".pdf") and file not in files_to_remove:
            pdf_files.append(file)

    pdf_files_sorted = sorted(pdf_files)
    return pdf_files_sorted
    # return ["Sample-C10-001.pdf"]
