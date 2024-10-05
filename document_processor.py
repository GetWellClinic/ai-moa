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

from workflow import Workflow

class DocumentProcessor:
    def __init__(self, base_url, session, last_pending_doc_file, enable_ocr_gpu):
        self.base_url = base_url
        self.session = session
        self.enable_ocr_gpu = enable_ocr_gpu
        self.last_pending_doc_file = last_pending_doc_file

    def get_file_content(self, doc_no):
        file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={doc_no}"
        file_response = self.session.get(file_url)
        if file_response.status_code == 200 and file_response.content:
            with open("downloaded_document.pdf", "wb") as file:
                file.write(file_response.content)
            return True
        else:
            print("Failed to fetch file content. Status code:", file_response.status_code)
            return False

    def process_documents(self, driver, login_url, login_successful_callback):
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            return self.last_pending_doc_file

        driver.get(f"{self.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
        script_value = driver.execute_script("return typeDocLab;")

        for doc_no in script_value['DOC']:
            if doc_no > self.last_pending_doc_file:
                if self.process_single_document(doc_no):
                    self.last_pending_doc_file = doc_no

        return self.last_pending_doc_file

    def process_single_document(self, doc_no):
        if self.get_file_content(doc_no):
            workflow = Workflow("downloaded_document.pdf", self.session, self.base_url, doc_no, self.enable_ocr_gpu)
            workflow.execute_tasks_from_csv()
            return True
        print(f"Failed to process document {doc_no}")
        return False
