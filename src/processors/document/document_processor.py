import logging
from .base_document_processor import BaseDocumentProcessor
from .local_file_processor import LocalFileProcessor
from .o19_processor import O19Processor

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, config):
        self.config = config
        processor_type = config.get('document_processor.type', 'local')
        if processor_type == 'local':
            self.processor = LocalFileProcessor(config)
        elif processor_type == 'o19':
            self.processor = O19Processor(config)
        else:
            raise ValueError(f"Unknown processor type: {processor_type}")

    def process_documents(self, login_url, login_successful_callback):
        return self.processor.process_documents(login_url, login_successful_callback)

    def get_file_content(self, name):
        return self.processor.get_file_content(name)
