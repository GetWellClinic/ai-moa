# COPYRIGHT © 2024 by Spring Health Corporation <office(at)springhealth.org>
# Toronto, Ontario, Canada
# SUMMARY: This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software,
# documentation, and configuration files.
# These programs, documentation, and configuration files are made available to you as open source
# in the hopes that your clinic or organization may find it useful and improve your care to the public
# by reducing administrative burden for your staff and service providers. 
# NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
# and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
# LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
# Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.
# ***
# NOTICE: We hope that you will consider contributing to our common source code repository so that
# others may benefit from your shared work.
# However, if you distribute this code or serve this application to users in modified form,
# or as part of a derivative work, you are required to make your modified or derivative work
# source code available under the same herein described license.
# Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work
# source code can be acquired publicly in its latest most up-to-date version, within one month.
# ***

import os
from ocr_utils import has_ocr, extract_text_doctr, extract_text_from_pdf_file
from workflow import Workflow
import logging

import logging

class PdfProcessor:
    def __init__(self, base_url, session, last_processed_pdf,enable_ocr_gpu):
        self.base_url = base_url
        self.session = session
        self.last_processed_pdf = last_processed_pdf
        self.enable_ocr_gpu = enable_ocr_gpu
        self.logger = logging.getLogger(__name__)

    def get_pdf_content(self, pdf_name):
        self.logger.debug(f"Fetching PDF content for: {pdf_name}")
        pdf_url = f"{self.base_url}/dms/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir=File&queueId=1&pdfName={pdf_name}"
        pdf_response = self.session.get(pdf_url)
        if pdf_response.status_code == 200:
            return pdf_response.content
        else:
            self.logger.error(f"Failed to fetch PDF content. Status code: {pdf_response.status_code}")
            return None

    def process_pdfs(self, driver, login_url, login_successful_callback):
        self.logger.info("Starting PDF processing")
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            self.logger.error("Login failed.")
            return self.last_processed_pdf

        self.logger.info("Login successful!")
        driver.get(f"{self.base_url}/dms/incomingDocs.jsp")
        driver.execute_script("loadPdf('1', 'File');")
        driver.implicitly_wait(10)

        pdf_list = self.get_pdf_list(driver)
        update_time = self.process_pdf_list(pdf_list)

        self.logger.info("PDF processing completed")
        return update_time

    def get_pdf_list(self, driver):
        select_element = driver.find_element_by_id("SelectPdfList")
        return [option for option in select_element.find_elements_by_tag_name('option') if option.get_attribute('value')]

    def process_pdf_list(self, pdf_list):
        self.logger.info("Processing PDF list")
        update_time = self.last_processed_pdf or pdf_list[0].text.split(") ", 1)[1]

        for option in pdf_list:
            current_time = option.text.split(") ", 1)[1]
            if current_time > update_time:
                update_time = current_time
                self.process_single_pdf(option.get_attribute('value'))

        return update_time

    def process_single_pdf(self, pdf_name):
        self.logger.debug(f"Processing single PDF: {pdf_name}")
        pdf_content = self.get_pdf_content(pdf_name)
        if pdf_content:
            with open("downloaded_pdf.pdf", "wb") as f:
                f.write(pdf_content)
            workflow = Workflow("downloaded_pdf.pdf", self.session, self.base_url, pdf_name, self.enable_ocr_gpu)
            workflow.execute_tasks_from_csv()
            os.remove("downloaded_pdf.pdf")
        else:
            self.logger.error(f"Failed to fetch PDF content for: {pdf_name}")
        self.logger.info("PDF processing completed")
        self.logger.info("PDF processing completed")
        self.logger.info("Processing PDF list")
        self.logger.debug(f"Processing single PDF: {pdf_name}")
