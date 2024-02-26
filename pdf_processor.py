from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime

class PdfProcessor:
    def __init__(self, base_url, session, last_processed_pdf):
        self.base_url = base_url
        self.session = session
        self.last_processed_pdf = last_processed_pdf

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
            exit()
        else:
            print("Login successful!")

        driver.get(f"{self.base_url}/dms/incomingDocs.jsp")
        driver.execute_script("loadPdf('1', 'File');")
        driver.implicitly_wait(10)
        select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

        update_time = ""

        for option in select_element.options:
            if(option.get_attribute('value') != ""):
                split_string = option.get_attribute('text').split(") ", 1)
                if(self.last_processed_pdf == ""):
                    update_time = split_string[1]
                else:
                    update_time = self.last_processed_pdf

                last_file = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
                current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")

                if last_file <= current_file:
                    pdf_content = self.get_pdf_content(option.get_attribute('value'))
                    if pdf_content:
                        with open("downloaded_pdf.pdf", "wb") as f:
                            f.write(pdf_content)
                        print("PDF Content:", pdf_content)

                        url = f"{self.base_url}/demographic/SearchDemographic.do"

                        # Define the payload data
                        payload = {
                            "query": "test"
                        }

                        # Send the POST request
                        response = self.session.post(url, data=payload)

                        url = f"{self.base_url}/dms/ManageDocument.do"

                        # Define the parameters
                        params = {
                            "method": "addIncomingDocument",
                            "pdfDir": "File",
                            "pdfName": "sample.pdf",
                            "queueId": "1",
                            "pdfNo": "1",
                            "queue": "1",
                            "pdfAction": "",
                            "lastdemographic_no": "1",
                            "entryMode": "Fast",
                            "docType": "lab",
                            "docClass": "Cardio Respiratory Report",
                            "docSubClass": "",
                            "documentDescription": "this is a test",
                            "observationDate": "2024-02-09",
                            "saved": "false",
                            "demog": "1",
                            "demographicKeyword": "TEST, PATIENT (1961-12-23)",
                            "provi": "999998",
                            "flagproviders":"999998",
                            "MRPNo": "",
                            "MRPName": "undefined",
                            "ProvKeyword": "",
                            "save": "Save & Next"
                        }

                        # Send the POST request
                        response = self.session.post(url, data=params)
