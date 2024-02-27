import csv
import random
import fitz
import PyPDF2

class Workflow:
    def __init__(self, filepath):
        self.filepath = filepath
        self.tesseracted_text = None

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
            return True
        except Exception as e:
            print("An error occurred:", e)
            return False

    def ask_ai(self,param,additional_param=None):
        print(f"Executing ask_ai with parameter: {param}, additional_param={additional_param}")
        return random.choice([True, False]),"test"

    def flag_email(self,param):
        print(f"Executing flag_email with parameter: {param}")
        return random.choice([True, False])

    def get_patient_details(self,param1, param2,additional_param=None):
        print(f"Executing get_patient_details with parameters: {param1}, {param2}, additional_param={additional_param}")
        return random.choice([True, True]),"1245dsd"

    def update_oscar(self,param1, param2, additional_param=None):
        print(f"Executing update_oscar with parameters: {param1}, {param2}, additional_param={additional_param}")
        return random.choice([True, True])


    def execute_task(self,task, previous_result=None):
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
                    return false_next_row,response[1]
            else:
                return true_next_row if response else false_next_row 
        else:
            print(f"Error: Function {function_name} not found or not callable.")
            return false_next_row 

    def execute_tasks(self,tasks, current_row, previous_result=None):
        if current_row >= len(tasks):
            print("Reached end of tasks.")
            return

        next_row = self.execute_task(tasks[current_row], previous_result)
        if next_row == 'exit':
            print("Exiting task execution.")
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

    def execute_tasks_from_csv(self):
        tasks = self.read_tasks_from_csv('workflow.csv')
        print(self.filepath)
        self.execute_tasks(tasks, 0)
