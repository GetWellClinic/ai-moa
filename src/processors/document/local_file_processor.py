import os
from .base_document_processor import BaseDocumentProcessor

class LocalFileProcessor(BaseDocumentProcessor):
    def __init__(self, config):
        self.config = config
        self.input_directory = config.get('document_processor.local.input_directory', '/app/input')

    def login(self, login_url, login_successful_callback):
        # No login needed for local files
        pass

    def get_file_content(self, name):
        file_path = os.path.join(self.input_directory, name)
        try:
            with open(file_path, 'rb') as file:
                return file.read()
        except IOError as e:
            print(f"Error reading file {name}: {e}")
            return None

    def process_documents(self, login_url, login_successful_callback):
        processed_files = []
        for filename in os.listdir(self.input_directory):
            if self.get_file_content(filename):
                processed_files.append(filename)
        return processed_files
