import os
from .base_pdf_fetcher import BasePdfFetcher

class LocalPdfFetcher(BasePdfFetcher):
    """
    Fetches PDF content from the local filesystem.
    """

    def __init__(self, config):
        self.config = config
        self.input_directory = config.get('file_processing.input_directory')

    def get_pdf_content(self, name):
        file_path = os.path.join(self.input_directory, name)
        try:
            with open(file_path, 'rb') as file:
                return file.read()
        except IOError as e:
            print(f"Error reading file {name}: {e}")
            return None
