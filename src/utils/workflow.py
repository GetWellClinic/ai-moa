"""
Module for managing the workflow of processing medical documents.

This module contains the Workflow class which handles various operations such as OCR,
patient information extraction, and interaction with the Oscar EMR system using Huey for task queuing.

The module provides functionality to:
1. Process and categorize medical documents
2. Perform OCR on PDF files
3. Extract patient and doctor information
4. Interact with the Oscar EMR system
5. Execute workflow tasks based on configuration

Dependencies:
- Various Python libraries including re, torch, fitz, PyPDF2, requests, json, datetime, logging, time
- doctr for OCR
- BeautifulSoup for HTML parsing
- PIL and pytesseract for image processing
- utils.config_manager for configuration management
- huey for task queuing
"""

import re
import time
from typing import Dict, Any, List

import fitz
import PyPDF2
import requests
import torch
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from huey import task

from src.config import ConfigManager


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

    def __init__(self, session, config: ConfigManager):
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
        self.logger = config.setup_logging()
        self.base_url = config.get('emr',{}).get('base_url')
        self.url = config.get('ai_config', {}).get('url')
        self.headers = {
            "Authorization": f"Bearer {config.get('ai_config', {}).get('auth_token')}",
            "Content-Type": "application/json"
        }
        self.categories = config.document_categories
        self.categories_code = [cat.replace(' ', '') for cat in self.categories]
        self._setup_pytesseract()

    def _setup_pytesseract(self):
        """
        Set up pytesseract with the configured path.
        """
        tesseract_path = self.config.get('ocr', {}).get('tesseract_path')
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            self.logger.warning("Tesseract path not configured. Using default path.")

    def find_category_index(self, text: str) -> bool:
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
        text = text.replace('.', '').lower()
        for word in text.split():
            word = word.replace('"', '').replace("'", "")
            for index, category in enumerate(self.categories_code):
                if word == category.lower():
                    self.logger.debug(f"Category index found: {index}")
                    self.fileType = category.lower()
                    self.execute_tasks_from_config(index)
                    return True
        self.logger.debug("No category found, setting to 'others'")
        self.fileType = 'others'
        self.execute_tasks_from_config(self.categories_code.index('Others'))
        return False

    def has_ocr(self) -> bool:
        """
        Check if the PDF file has an OCR layer.

        This method attempts to extract text from each page of the PDF.
        If any page contains text, it assumes the PDF has an OCR layer.

        Returns:
            bool: True if the PDF has an OCR layer, False otherwise.
        """
        pdf_path = self.filepath
        try:
            with fitz.open(pdf_path) as pdf_document:
                for page in pdf_document:
                    if page.get_text().strip():
                        return True
            return False
        except Exception as e:
            self.logger.error(f"An error occurred in has_ocr: {e}")
            return False

    def extract_text_from_pdf(self) -> bool:
        """
        Extract text from PDF using pytesseract OCR.

        This method processes each page of the PDF, converts it to an image,
        and then uses pytesseract to perform OCR on the image.

        Returns:
            bool: True if text extraction was successful, False otherwise.
        """
        pdf_path = self.filepath
        try:
            pdf_document = fitz.open(pdf_path)
            extracted_text = ''
            for page in pdf_document:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                extracted_text += pytesseract.image_to_string(img) + '\n'
            self.tesseracted_text = extracted_text
            return True
        except Exception as e:
            self.logger.error(f"An error occurred in extract_text_from_pdf: {e}")
            return False

    def extract_text_doctr(self) -> bool:
        """
        Extract text from PDF using doctr OCR.

        This method uses the doctr library to perform OCR on the PDF file.
        It supports GPU acceleration if enabled in the configuration.

        Returns:
            bool: True if text extraction was successful, False otherwise.
        """
        start_time = time.time()
        pdf_path = self.filepath
        self.logger.debug(f"Processing PDF: {pdf_path}")
        try:
            device = torch.device(
                "cuda:0" if self.config.get('ocr', {}).get('enable_gpu') and torch.cuda.is_available() else "cpu")
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

    def _process_ocr_result(self, result) -> str:
        """
        Process the OCR result from doctr.

        This method extracts text from the OCR result, organizing it by pages and lines.

        Args:
            result: The OCR result from doctr.

        Returns:
            str: Processed text from the OCR result.
        """
        text = []
        for page in result.pages:
            self.logger.debug(f"Processing page {page.page_idx}")
            page_text = []
            for block in page.blocks:
                for line in block.lines:
                    page_text.append(' '.join(word.value for word in line.words))
            text.append('\n'.join(page_text))
        return '\n\n'.join(text)

    def extract_text_from_pdf_file(self) -> bool:
        """
        Extract text from PDF file using PyPDF2.

        This method is used when the PDF already has a text layer and OCR is not needed.

        Returns:
            bool: True if text extraction was successful, False otherwise.
        """
        pdf_path = self.filepath
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''.join(page.extract_text() for page in reader.pages)
            self.tesseracted_text = text
            return True
        except Exception as e:
            self.logger.error(f"An error occurred in extract_text_from_pdf_file: {e}")
            return False

    def build_prompt(self, prompt: str) -> bool:
        """
        Build and send a prompt to the AI model.

        This method prepares the data for the AI model, sends the request,
        and processes the response.

        Args:
            prompt (str): The prompt to send to the AI model.

        Returns:
            bool: True if the prompt was successfully processed, False otherwise.
        """
        data = self._prepare_prompt_data(prompt)
        try:
            return self._send_prompt_request(data)
        except requests.RequestException as e:
            self.logger.error(f"Error in build_prompt: {e}")
            return False

    def _prepare_prompt_data(self, prompt: str) -> Dict[str, Any]:
        """
        Prepare the data for the AI model prompt.

        Args:
            prompt (str): The prompt to include in the data.

        Returns:
            Dict[str, Any]: Prepared data for the AI model request.
        """
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

    def _send_prompt_request(self, data: Dict[str, Any]) -> bool:
        """
        Send the prompt request to the AI model and process the response.

        Args:
            data (Dict[str, Any]): The prepared data for the AI model request.

        Returns:
            bool: True if the request was successful and processed, False otherwise.

        Raises:
            requests.RequestException: If there's an error in the HTTP request.
        """
        response = requests.post(self.url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        content_value = response.json()['choices'][0]['message']['content']
        self.logger.debug("LLM response content: %s", content_value)
        self.find_category_index(content_value)
        return True

    @task()
    def execute_task(self, task: Dict[str, Any], previous_result: Any = None) -> Any:
        """
        Execute a single task in the workflow.

        This method is decorated as a Huey task. It dynamically calls the appropriate
        method based on the task definition and handles the task's outcome.

        Args:
            task (Dict[str, Any]): A dictionary containing task details.
            previous_result: The result from the previous task, if any.

        Returns:
            Any: The result of the task execution.
        """
        function_name = task['name']
        params = task.get('params', [])
        self.logger.debug(f"Executing task: {function_name}")
        function_to_call = getattr(self, function_name, None)

        if function_to_call and callable(function_to_call):
            self.logger.info(f"Executing function: {function_name} with parameters: {params}")

            try:
                if 'additional_param' in function_to_call.__code__.co_varnames:
                    response = function_to_call(*params, additional_param=previous_result)
                else:
                    response = function_to_call(*params)

                self.logger.debug(f"Response from {function_name}: {response}")
                return response
            except Exception as e:
                self.logger.error(f"Error executing function {function_name}: {str(e)}")
                return False
        else:
            self.logger.error(f"Error: Function {function_name} not found or not callable.")
            return False

    def execute_workflow(self):
        """
        Execute the entire workflow.

        This method starts the workflow execution from the first step and continues
        until reaching the 'exit' step or encountering an error.
        """
        self.logger.info("Executing workflow")
        workflow_steps = self.config.workflow_steps
        current_step = workflow_steps[0]
        while current_step['name'] != 'exit':
            self.logger.info(f"Executing step: {current_step['name']}")
            result = self.execute_task(current_step)
            current_step = self._get_next_step(current_step, result)
            if current_step is None:
                self.logger.error(f"No next step defined for {current_step['name']}")
                break
        self.logger.info("Workflow execution completed")

    def _get_next_step(self, current_step: Dict[str, Any], outcome: bool) -> Dict[str, Any]:
        """
        Get the next step based on the current step and its outcome.

        Args:
            current_step (Dict[str, Any]): The current step information.
            outcome (bool): The outcome of the current step (True or False).

        Returns:
            Dict[str, Any]: The next step information, or None if not found.
        """
        next_step_name = current_step['true_next'] if outcome else current_step['false_next']
        workflow_steps = self.config.workflow_steps
        for step in workflow_steps:
            if step['name'] == next_step_name:
                return step
        return None

    def execute_tasks_from_config(self, index: int):
        """
        Execute tasks defined in the configuration.

        This method reads tasks from the configuration and executes them.

        Args:
            index (int): Index to determine which set of tasks to execute.
        """
        tasks = self.config.get_tasks_for_category(index)
        self.logger.debug(f"Processing file: {self.filepath}")
        for task in tasks:
            self.execute_task(task)

    # Add other methods as needed, each with proper type hints and docstrings
