import csv
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class WorkflowProcessor:
    def __init__(self, filepath, session, base_url, file_name, enable_ocr_gpu):
        self.filepath = filepath
        self.session = session
        self.base_url = base_url
        self.file_name = file_name
        self.enable_ocr_gpu = enable_ocr_gpu
        self.patient_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.document_description = ''
        self.tesseracted_text = None
        self.url = "http://127.0.0.1:5000/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer qwerty",
            "Content-Type": "application/json"
        }
        self.categories = [
            "Lab", "Consult", "Insurance", "Legal", "Old Chart", "Radiology",
            "Pathology", "Others", "Photo", "Consent", "Diagnostics", "Pharmacy",
            "Requisition", "Referral", "Request"
        ]
        self.categories_code = [
            "Lab", "Consult", "Insurance", "Legal", "OldChart", "Radiology",
            "Pathology", "Others", "Photo", "Consent", "Diagnostics", "Pharmacy",
            "Requisition", "Referral", "Request"
        ]

    # Add other methods from the original Workflow class here
import csv
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class WorkflowProcessor:
    def __init__(self, filepath, session, base_url, file_name, enable_ocr_gpu):
        self.filepath = filepath
        self.session = session
        self.base_url = base_url
        self.file_name = file_name
        self.enable_ocr_gpu = enable_ocr_gpu
        self.patient_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.document_description = ''
        self.tesseracted_text = None
        self.url = "http://127.0.0.1:5000/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer qwerty",
            "Content-Type": "application/json"
        }
        self.categories = [
            "Lab", "Consult", "Insurance", "Legal", "Old Chart", "Radiology",
            "Pathology", "Others", "Photo", "Consent", "Diagnostics", "Pharmacy",
            "Requisition", "Referral", "Request"
        ]
        self.categories_code = [
            "Lab", "Consult", "Insurance", "Legal", "OldChart", "Radiology",
            "Pathology", "Others", "Photo", "Consent", "Diagnostics", "Pharmacy",
            "Requisition", "Referral", "Request"
        ]

    # Add other methods from the original Workflow class here
