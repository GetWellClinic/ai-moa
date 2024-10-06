"""
Module for managing the workflow of processing medical documents.

This module contains the Workflow class which handles various operations such as OCR,
patient information extraction, and interaction with the Oscar EMR system using Huey for task queuing.

The module provides functionality to:
1. Process and categorize medical documents
2. Perform OCR on PDF files
3. Extract patient and doctor information
4. Interact with the Oscar EMR system
5. Execute workflow tasks based on CSV configurations

Dependencies:
- Various Python libraries including csv, re, torch, fitz, PyPDF2, requests, json, datetime, logging, time
- doctr for OCR
- BeautifulSoup for HTML parsing
- PIL and pytesseract for image processing
- utils.config_manager for configuration management
- huey for task queuing
"""

# [Your existing import statements here]

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

    def __init__(self, session, config):
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
        self.logger = logging.getLogger(__name__)
        self.base_url = config.get('base_url')
        self.url = config.get('ai_config', {}).get('url')
        self.headers = {
            "Authorization": f"Bearer {config.get('ai_config', {}).get('auth_token')}",
            "Content-Type": "application/json"
        }
        self.categories = config.get('document_categories', [])
        self.categories_code = [cat.replace(' ', '') for cat in self.categories]

    def find_category_index(self, text):
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
                    self.execute_tasks_from_csv(index)
                    return True
        self.logger.debug("No category found, setting to 'others'")
        self.fileType = 'others'
        self.execute_tasks_from_csv(self.categories_code.index('Others'))
        return False

    def has_ocr(self):
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

    def extract_text_from_pdf(self):
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

    def extract_text_doctr(self):
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
            device = torch.device("cuda:0" if self.config.get('enable_ocr_gpu') and torch.cuda.is_available() else "cpu")
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

    def _process_ocr_result(self, result):
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

    def extract_text_from_pdf_file(self):
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

    def build_prompt(self, prompt):
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

    def _prepare_prompt_data(self, prompt):
        """
        Prepare the data for the AI model prompt.

        Args:
            prompt (str): The prompt to include in the data.

        Returns:
            dict: Prepared data for the AI model request.
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

    def _send_prompt_request(self, data):
        """
        Send the prompt request to the AI model and process the response.

        Args:
            data (dict): The prepared data for the AI model request.

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

    # [Rest of your methods here, each with detailed docstrings]

    @task()
    def execute_task(self, task, previous_result=None):
        """
        Execute a single task in the workflow.

        This method is decorated as a Huey task. It dynamically calls the appropriate
        method based on the task definition and handles the task's outcome.

        Args:
            task (tuple): A tuple containing task details (number, function name, parameters, next steps).
            previous_result: The result from the previous task, if any.

        Returns:
            tuple or str: The next task number and any additional results, or just the next task number.
        """
        task_number, function_name, *params, true_next_row, false_next_row = task
        self.logger.debug(f"Executing task {task_number}: {function_name}")
        function_to_call = getattr(self, function_name, None)
        
        if function_to_call and callable(function_to_call):
            self.logger.info(f"Executing Task {task_number} with function: {function_name} and parameters: {', '.join(params)}")
            
            try:
                if 'additional_param' in function_to_call.__code__.co_varnames:
                    response = function_to_call(*params, additional_param=previous_result)
                else:
                    response = function_to_call(*params)

                self.logger.debug(f"Response from {function_name}: {response}")

                if isinstance(response, tuple) and len(response) > 1:
                    return (true_next_row, response[1]) if response[0] else (false_next_row, response[1])
                else:
                    return true_next_row if response else false_next_row
            except Exception as e:
                self.logger.error(f"Error executing function {function_name}: {str(e)}")
                return false_next_row
        else:
            self.logger.error(f"Error: Function {function_name} not found or not callable.")
            return false_next_row

    def execute_tasks(self, tasks, current_row, previous_result=None):
        """
        Execute a series of tasks in the workflow.

        This method recursively executes tasks based on their outcomes and the defined workflow.

        Args:
            tasks (list): List of tasks to execute.
            current_row (int): The index of the current task in the tasks list.
            previous_result: The result from the previous task, if any.
        """
        if current_row >= len(tasks):
            self.logger.info("Reached end of tasks.")
            return

        next_row = self.execute_task(tasks[current_row], previous_result)
        if next_row == 'exit':
            self.logger.info("Exiting task execution.")
            return

        if isinstance(next_row, tuple):
            next_row_index, next_result = next_row
            self.execute_tasks(tasks, int(next_row_index), previous_result=next_result)
        elif next_row:
            next_row_parts = next_row.split(",")
            next_row_index = int(next_row_parts[0])
            next_result = next_row_parts[1] if len(next_row_parts) > 1 else None
            self.execute_tasks(tasks, next_row_index, previous_result=next_result)

    def read_tasks_from_csv(self, file_path):
        """
        Read tasks from a CSV file.

        Args:
            file_path (str): Path to the CSV file containing task definitions.

        Returns:
            list: List of tasks read from the CSV file.
        """
        tasks = []
        self.logger.debug(f"Reading tasks from CSV: {file_path}")
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                tasks.append(row)
        return tasks

    def execute_tasks_from_csv(self, index=None):
        """
        Execute tasks defined in a CSV file.

        This method reads tasks from a CSV file and executes them.

        Args:
            index (int, optional): Index to determine which CSV file to use.
        """
        if index is None:
            tasks = self.read_tasks_from_csv(self.config.get('workflow', {}).get('file_path', 'workflow.csv'))
        else:
            tasks = self.read_tasks_from_csv(f"{index}.csv")
        self.logger.debug(f"Processing file: {self.filepath}")
        self.execute_tasks(tasks, 0)

    def execute_workflow(self):
        """
        Execute the entire workflow.

        This method starts the workflow execution from the first step and continues
        until reaching the 'exit' step or encountering an error.
        """
        self.logger.info("Executing workflow")
        current_step = self.workflow_config.workflow_steps[0]['name']
        while current_step != 'exit':
            self.logger.info(f"Executing step: {current_step}")
            result = self.execute_step(current_step)
            current_step = self.workflow_config.get_next_step(current_step, result)
            if current_step is None:
                self.logger.error(f"No next step defined for {current_step}")
                break
        self.logger.info("Workflow execution completed")

    @task()
    def execute_step(self, step_name):
        """
        Execute a single step in the workflow.

        This method is decorated as a Huey task. It dynamically calls the method
        corresponding to the step name.

        Args:
            step_name (str): Name of the step to execute.

        Returns:
            bool: True if the step executed successfully, False otherwise.
        """
        function_to_call = getattr(self, step_name, None)
        if function_to_call and callable(function_to_call):
            try:
                result = function_to_call()
                self.logger.info(f"Step {step_name} completed with result: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error executing step {step_name}: {str(e)}")
                return False
        else:
            self.logger.error(f"Error: Function {step_name} not found or not callable.")
            return False
