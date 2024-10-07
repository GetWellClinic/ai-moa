from abc import ABC, abstractmethod

class BasePdfFetcher(ABC):
    @abstractmethod
    def get_pdf_content(self, name):
        pass
