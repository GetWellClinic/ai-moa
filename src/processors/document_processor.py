import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.workflow import Workflow


class DocumentProcessor:
    """Class for processing documents in the Oscar EMR system."""

    def __init__(self, config, session_manager):
        """Initialize DocumentProcessor with configuration and session manager."""
        self.config = config
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)

    def get_file_content(self, doc_no):
        """Fetch the content of a document file from the Oscar EMR system."""
        self.logger.debug(f"Fetching file content for document number: {doc_no}")
        file_url = f"{self.config.base_url}/dms/ManageDocument.do?method=display&doc_no={doc_no}"
        file_response = self.session_manager.get_session().get(file_url)
        if file_response.status_code == 200 and file_response.content:
            with open("downloaded_document.pdf", "wb") as file:
                file.write(file_response.content)
            return True
        else:
            self.logger.error(f"Failed to fetch file content. Status code: {file_response.status_code}")
            return False

    def process_documents(self, driver, login_url, login_successful_callback):
        """Process all documents in the Oscar EMR system."""
        self.logger.info("Starting document processing")
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.config.base_url}/login.do":
            self.logger.error("Login failed.")
            return self.config.last_pending_doc_file

        driver.get(f"{self.config.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "typeDocLab")))
        script_value = driver.execute_script("return typeDocLab;")

        for doc_no in script_value['DOC']:
            self.logger.debug(f"Processing document number: {doc_no}")
            if int(doc_no) > int(self.config.last_pending_doc_file):
                if self.process_single_document(doc_no):
                    self.config.last_pending_doc_file = doc_no

        self.logger.info("Document processing completed")
        return self.config.last_pending_doc_file

    def process_single_document(self, doc_no):
        """Process a single document file."""
        self.logger.debug(f"Processing single document: {doc_no}")
        if self.get_file_content(doc_no):
            workflow = Workflow(
                "downloaded_document.pdf",
                self.session_manager.get_session(),
                self.config.base_url,
                doc_no,
                self.config.enable_ocr_gpu
            )
            workflow.execute_tasks_from_csv()
            return True
        self.logger.error(f"Failed to process document {doc_no}")
        return False
