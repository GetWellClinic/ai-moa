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
from huey import crontab, MemoryHuey
from config import ConfigManager
from auth import LoginManager, SessionManager
from ai_moa_utils import setup_logging
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
from ..utils import local_files
from ..utils import ocr
from ..utils import llm
from ..o19 import o19_updater, o19_inbox
from ..document_tagger import document_category, get_document_description
from ..provider_tagger import provider
from ..patient_tagger import patient

huey: MemoryHuey = MemoryHuey('aimoa_automation')

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
    def __init__(self, config: ConfigManager, session_manager: SessionManager, login_manager: LoginManager):
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
        self.default_values = config.default_values
        self.patient_name = ''
        self.fl_name = ''
        self.fileType = ''
        self.demographic_number = ''
        self.mrp = ''
        self.provider_number = []
        self.document_description = ''
        self.filepath = config.get('document_processor.local.input_directory', '/app/input')
        self.ocr_text = None
        self.session = session_manager.get_session()
        self.login_manager = login_manager
        self.base_url = config.get('emr.base_url')
        self.file_name = ''
        self.enable_ocr_gpu = config.get('enable_ocr_gpu', True)
        self.url = config.get('ai.uri', "https://localhost:3334/v1/chat/completions")
        self.headers = {
            "Authorization": f"Bearer {config.get('ai.api_key')}",
            "Content-Type": "application/json"
        }
        self.update_o19 = o19_updater.update_o19
        self.update_o19_pendingdocs = o19_updater.update_o19_pendingdocs
        self.update_o19_incomingdocs = o19_updater.update_o19_incomingdocs
        self.update_o19_last_processed_file = o19_updater.update_o19_last_processed_file
        self.check_lock = o19_inbox.check_lock
        self.release_lock = o19_inbox.release_lock
        self.get_document_processor_type = o19_inbox.get_document_processor_type
        self.get_o19_documents = o19_inbox.get_o19_documents
        self.get_driver = o19_inbox.get_driver
        self.get_inbox_pendingdocs_documents = o19_inbox.get_inbox_pendingdocs_documents
        self.get_inbox_incomingdocs_documents = o19_inbox.get_inbox_incomingdocs_documents
        self.get_local_documents = local_files.get_local_documents
        self.has_ocr = ocr.has_ocr
        self.extract_text_doctr = ocr.extract_text_doctr
        self.query_prompt = llm.query_prompt
        self.get_category_types = document_category.get_category_types
        self.get_category_type = document_category.get_category_type
        self.get_document_description = document_category.get_document_description
        self.get_provider_list = provider.get_provider_list
        self.get_provider_list_filemode = provider.get_provider_list_filemode
        self.get_patient_hin = patient.get_patient_hin
        self.get_patient_dob = patient.get_patient_dob
        self.get_patient_name = patient.get_patient_name
        self.unidentified_patients = patient.unidentified_patients
        self.filter_results = patient.filter_results
        self.get_patient_Html_Common = patient.get_patient_Html_Common
        self.convert_date = patient.convert_date
        self.get_patient_Html = patient.get_patient_Html


    # @huey.task()
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
            result = function_to_call(self)
            self.config.set_shared_state(step['name'], result)
            if isinstance(result, tuple):
                return result[0]
            else:
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

            # Find the index of the step to pop
            index_to_pop = None
            for index, step in enumerate(self.steps):
                if step['name'] == current_step['name']:
                    index_to_pop = index
                    break  # Exit the loop once the match is found

            # Pop the steps to avoid error in execution
            if index_to_pop is not None:
                self.steps = self.steps[index_to_pop + 1:]
            
            current_step = next((step for step in self.steps if step['name'] == next_step_name), None)
        
        self.logger.info("Workflow execution completed")