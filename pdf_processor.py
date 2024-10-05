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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
from workflow import Workflow

class PdfProcessor:
    def __init__(self, base_url, session, last_processed_pdf,enable_ocr_gpu):
        self.base_url = base_url
        self.session = session
        self.last_processed_pdf = last_processed_pdf
        self.enable_ocr_gpu = enable_ocr_gpu

    def get_pdf_content(self, name):
        pdf_url = f"{self.base_url}/dms/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir=File&queueId=1&pdfName={name}"
        pdf_response = self.session.get(pdf_url)
        if pdf_response.status_code == 200:
            return pdf_response.content
        else:
            print("Failed to fetch PDF content. Status code:", pdf_response.status_code)
            return None

    def process_pdfs(self, driver, login_url, login_successful_callback):
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            return None

        print("Login successful!")
        driver.get(f"{self.base_url}/dms/incomingDocs.jsp")
        driver.execute_script("loadPdf('1', 'File');")
        driver.implicitly_wait(10)
        select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

        update_time = self.last_processed_pdf

        for option in select_element.options:
            if option.get_attribute('value') != "":
                split_string = option.get_attribute('text').split(") ", 1)
                current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")
                last_file = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S") if update_time else current_file

                if last_file <= current_file:
                    update_time = split_string[1]
                    pdf_content = self.get_pdf_content(option.get_attribute('value'))
                    if pdf_content:
                        with open("downloaded_pdf.pdf", "wb") as f:
                            f.write(pdf_content)
                        workflow = Workflow("downloaded_pdf.pdf", self.session, self.base_url, option.get_attribute('value'), self.enable_ocr_gpu)
                        workflow.execute_tasks_from_csv()

        return update_time
