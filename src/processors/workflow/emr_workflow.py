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
    def execute_task(self, step: Dict[str, Any], previous_result: Any = None) -> Any:
        function_name = step['name']
        self.logger.info(f"Executing task: {function_name}")
        function_to_call = getattr(self, function_name, None)
        
        if function_to_call and callable(function_to_call):
            result = function_to_call(previous_result)
            self.task_results[step['name']] = result
            return result
        else:
            self.logger.error(f"Function {function_name} not found or not callable.")
            raise AttributeError(f"Function {function_name} not found or not callable.")

    def execute_workflow(self):
        self.logger.info("Starting workflow execution")
        current_step = self.steps[0]
        while current_step:
            previous_result = self.task_results.get(current_step.get('previous_step'))
            result = self.execute_task(current_step, previous_result)
            
            if result:
                next_step_name = current_step['true_next']
            else:
                next_step_name = current_step['false_next']
            
            if next_step_name == 'exit':
                self.logger.info("Workflow execution completed")
                return
            
            current_step = next((step for step in self.steps if step['name'] == next_step_name), None)
        
        self.logger.info("Workflow execution completed")

    def check_for_file(self, previous_result):
        input_directory = self.config.get('document_processor.local.input_directory', '/app/input')
        files = [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))]
        return len(files) > 0

    def has_ocr(self, previous_result):
        # Implementation
        pass

    def extract_text_from_pdf_file(self, previous_result):
        # Implementation
        pass

    def extract_text_doctr(self, previous_result):
        # Implementation
        pass

    def build_prompt(self, previous_result):
        # Implementation
        pass

    def get_document_description(self, previous_result):
        prompt = self.ai_prompts.get('get_document_description')
        # Use the prompt to get document description
        pass

    def getProviderList(self, previous_result):
        prompt = self.ai_prompts.get('getProviderList')
        # Use the prompt to get provider list
        pass

    def get_patient_name(self, previous_result):
        prompt = self.ai_prompts.get('get_patient_name')
        # Use the prompt to get patient name
        pass

    def set_patient(self, previous_result):
        # Implementation
        pass

    def set_doctor(self, previous_result):
        # Implementation
        pass

    def o19_update(self, previous_result):
        # Implementation
        pass
