import os
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.workflow import Workflow


class PdfProcessor:
    """Class for processing PDF documents in the Oscar EMR system."""

    def __init__(self, config, session_manager):
        """Initialize PdfProcessor with configuration and session manager."""
        self.config = config
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)

    def get_pdf_content(self, pdf_name):
        """Fetch the content of a PDF file from the Oscar EMR system."""
        self.logger.debug(f"Fetching PDF content for: {pdf_name}")
        pdf_url = (f"{self.config.base_url}/dms/ManageDocument.do?"
                   f"method=displayIncomingDocs&curPage=1&pdfDir=File&queueId=1&pdfName={pdf_name}")
        pdf_response = self.session_manager.get_session().get(pdf_url)
        if pdf_response.status_code == 200:
            return pdf_response.content
        else:
            self.logger.error(f"Failed to fetch PDF content. Status code: {pdf_response.status_code}")
            return None

    def process_pdfs(self, driver, login_url, login_successful_callback):
        """Process all PDFs in the Oscar EMR system."""
        self.logger.info("Starting PDF processing")
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.config.base_url}/login.do":
            self.logger.error("Login failed.")
            return self.config.last_processed_pdf

        self.logger.info("Login successful!")
        driver.get(f"{self.config.base_url}/dms/incomingDocs.jsp")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SelectPdfList")))
        driver.execute_script("loadPdf('1', 'File');")

        pdf_list = self.get_pdf_list(driver)
        update_time = self.process_pdf_list(pdf_list)

        self.logger.info("PDF processing completed")
        return update_time

    def get_pdf_list(self, driver):
        """Get the list of PDFs available for processing."""
        select_element = driver.find_element(By.ID, "SelectPdfList")
        return [
            option for option in select_element.find_elements(By.TAG_NAME, 'option')
            if option.get_attribute('value')
        ]

    def process_pdf_list(self, pdf_list):
        """Process the list of PDFs, updating the last processed time."""
        self.logger.info("Processing PDF list")
        update_time = self.config.last_processed_pdf or pdf_list[0].text.split(") ", 1)[1]

        for option in pdf_list:
            current_time = option.text.split(") ", 1)[1]
            if current_time > update_time:
                update_time = current_time
                self.process_single_pdf(option.get_attribute('value'))

        return update_time

    def process_single_pdf(self, pdf_name):
        """Process a single PDF file."""
        self.logger.debug(f"Processing single PDF: {pdf_name}")
        pdf_content = self.get_pdf_content(pdf_name)
        if pdf_content:
            with open("downloaded_pdf.pdf", "wb") as f:
                f.write(pdf_content)
            workflow = Workflow(
                "downloaded_pdf.pdf",
                self.session_manager.get_session(),
                self.config.base_url,
                pdf_name,
                self.config.enable_ocr_gpu
            )
            workflow.execute_tasks_from_csv()
            os.remove("downloaded_pdf.pdf")
        else:
            self.logger.error(f"Failed to fetch PDF content for: {pdf_name}")
