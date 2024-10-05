from .workflow import Workflow

class DocumentProcessor:
    def __init__(self, base_url, session, last_pending_doc_file, enable_ocr_gpu):
        self.base_url = base_url
        self.session = session
        self.enable_ocr_gpu = enable_ocr_gpu
        self.last_pending_doc_file = last_pending_doc_file

    def get_file_content(self, name):
        file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={name}"
        file_response = self.session.get(file_url)
        if file_response.status_code == 200 and file_response.content:
            with open("downloaded_pdf.pdf", "wb") as file:
                file.write(file_response.content)
            return True
        print(f"Failed to fetch file content. Status code: {file_response.status_code}")
        return False

    def process_documents(self, driver, login_url, login_successful_callback):
        try:
            driver.get(login_url)
            current_url = login_successful_callback(driver)
            if current_url == f"{self.base_url}/login.do":
                print("Login failed.")
                return

            driver.get(f"{self.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
            script_value = driver.execute_script("return typeDocLab;")
            
            for item in script_value['DOC']:
                if int(item) > int(self.last_pending_doc_file):
                    if self.get_file_content(item):
                        workflow = Workflow("downloaded_pdf.pdf", self.session, self.base_url, item, self.enable_ocr_gpu)
                        workflow.execute_tasks_from_csv()
                        self.last_pending_doc_file = item
                    else:
                        print(f"Failed to process document {item}")

            return self.last_pending_doc_file
        except Exception as e:
            print(f"An error occurred: {e}")
            return self.last_pending_doc_file
