from abc import ABC, abstractmethod

class BaseDocumentProcessor(ABC):
    @abstractmethod
    def login(self, login_url, login_successful_callback):
        pass

    @abstractmethod
    def get_file_content(self, name):
        pass

    @abstractmethod
    def process_documents(self, login_url, login_successful_callback):
        pass
