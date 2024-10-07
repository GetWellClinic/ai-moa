import os
from .base_document_processor import BaseDocumentProcessor

class LocalFileProcessor(BaseDocumentProcessor):
    def __init__(self, config):
        self.config = config
        self.input_directory = config.get('file_processing.input_directory', '/app/input')

    def login(self, login_url, login_successful_callback):
        # O19 login code commented out:
        # logger.info("Attempting to log in to O19 EMR")
        # # Implementation for O19 login
        # # Set self.session if login is successful
        pass

    def get_file_content(self, name):
        # O19 code commented out:
        # if not self.session:
        #     logger.error("Not logged in. Cannot fetch file content.")
        #     return None
        #
        # logger.info(f"Fetching file content for document: {name}")
        # file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={name}"
        # ...

        # Local filesystem code:
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
