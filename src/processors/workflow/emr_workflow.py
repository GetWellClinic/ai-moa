from typing import Dict, Any, List
from huey import crontab, task
from config import ConfigManager

from logging import setup_logging
import os

class Workflow:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = setup_logging(config)
        self.task_results = {}
        self.steps = config.workflow_steps
        self.document_categories = config.document_categories
        self.ai_prompts = config.ai_prompts

    @task()
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
        current_file = self.config.get_shared_state('current_file')
        # Implementation using current_file
        pass

    def extract_text_from_pdf_file(self):
        current_file = self.config.get_shared_state('current_file')
        # Implementation using current_file
        pass

    def extract_text_doctr(self):
        current_file = self.config.get_shared_state('current_file')
        # Implementation using current_file
        pass

    def build_prompt(self):
        extracted_text = self.config.get_shared_state('extracted_text')
        # Implementation using extracted_text
        pass

    def get_document_description(self):
        prompt = self.ai_prompts.get('get_document_description')
        # Use the prompt to get document description
        # Store the result in shared state
        pass

    def getProviderList(self):
        prompt = self.ai_prompts.get('getProviderList')
        # Use the prompt to get provider list
        # Store the result in shared state
        pass

    def get_patient_name(self):
        prompt = self.ai_prompts.get('get_patient_name')
        # Use the prompt to get patient name
        # Store the result in shared state
        pass

    def set_patient(self):
        patient_name = self.config.get_shared_state('patient_name')
        # Implementation using patient_name
        pass

    def set_doctor(self):
        provider_list = self.config.get_shared_state('provider_list')
        # Implementation using provider_list
        pass

    def o19_update(self):
        # Implementation using various shared state data
        pass
