from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
from workflow import Workflow

class PdfProcessor:
    """
    A class to process PDFs from the EMR 
    Attributes:
        base_url (str): The base URL of the EMR web
        session (requests.Session): The session used to make HTTP requests.
        last_processed_pdf (str): The timestamp of the last processed PDF.
    """

    def __init__(self, base_url, session, last_processed_pdf):
        """
        Initializes the PdfProcessor with the base URL, session, and last processed PDF timestamp.

        Args:
            base_url (str): The base URL of the web application.
            session (requests.Session): The session used to make HTTP requests.
            last_processed_pdf (str): The timestamp of the last processed PDF.
        """
        self.base_url = base_url
        self.session = session
        self.last_processed_pdf = last_processed_pdf

    def get_pdf_content(self, name):
        """
        Fetches the content of a PDF from the server.

        Args:
            name (str): The name of the PDF to fetch.

        Returns:
            bytes: The content of the PDF if fetched successfully, None otherwise.
        """
        pdf_url = f"{self.base_url}/dms/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir=File&queueId=1&pdfName={name}"
        pdf_response = self.session.get(pdf_url)
        if pdf_response.status_code == 200:
            return pdf_response.content
        else:
            print("Failed to fetch PDF content. Status code:", pdf_response.status_code)
            return None

    def process_pdfs(self, driver, login_url, login_successful_callback):
        """
        Processes incoming PDFs from the web application.

        Args:
            driver (selenium.webdriver): The Selenium WebDriver instance.
            login_url (str): The URL of the login page.
            login_successful_callback (function): A callback function to check if login was successful.

        Returns:
            str: The timestamp of the last processed PDF.
        """
        # Navigate to the login page
        driver.get(login_url)
        
        # Check if login was successful using the provided callback
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            exit()
        else:
            print("Login successful!")

        # Navigate to the incoming documents page
        driver.get(f"{self.base_url}/dms/incomingDocs.jsp")
        
        # Load the PDF list
        driver.execute_script("loadPdf('1', 'File');")
        
        # Wait for the PDF list to load
        driver.implicitly_wait(10)
        
        # Locate the PDF list dropdown
        select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

        update_time = ""

        # Iterate through each option in the dropdown
        for option in select_element.options:
            if option.get_attribute('value') != "":
                split_string = option.get_attribute('text').split(") ", 1)
                if self.last_processed_pdf == "":
                    update_time = split_string[1]
                else:
                    update_time = self.last_processed_pdf

                # Convert timestamps to datetime objects for comparison
                last_file = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
                current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")

                # Process PDFs that are new or updated
                if last_file <= current_file:
                    update_time = split_string[1]

                    # Fetch the PDF content
                    pdf_content = self.get_pdf_content(option.get_attribute('value'))
                    if pdf_content:
                        # Save the PDF content to a file
                        with open("downloaded_pdf.pdf", "wb") as f:
                            f.write(pdf_content)
                        print("PDF Content:", pdf_content)
                        
                        # Execute workflow tasks using the Workflow class
                        workflow = Workflow("downloaded_pdf.pdf", self.session, self.base_url, option.get_attribute('value'))
                        workflow.execute_tasks_from_csv()

        return update_time
