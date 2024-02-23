class DocumentProcessor:
    def __init__(self, base_url, session):
        self.base_url = base_url
        self.session = session

    def get_file_content(self, name):
        file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={name}"
        file_response = self.session.get(file_url)
        if file_response.status_code == 200:
            content_type = file_response.headers.get("content-type")
            file_extension = content_type.split("/")[-1] if content_type else "txt"
            filename = f"{name}.{file_extension}"
            with open(filename, "wb") as file:
                file.write(file_response.content)
            print("File saved as:", filename)
            return filename
        else:
            print("Failed to fetch file content. Status code:", file_response.status_code)
            return None

    def process_documents(self, driver, login_url, login_successful_callback):
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            print("Login failed.")
            return

        driver.get(f"{self.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
        script_value = driver.execute_script("return typeDocLab;")
        print(script_value)

        filename = self.get_file_content("30")
        if filename:
            url = f"{self.base_url}/dms/ManageDocument.do"
            payload = {
                "method": "documentUpdateAjax",
                "documentId": "18",
                "docType": "insurance",
                "documentDescription": "test",
                "observationDate": "2024/01/29",
                "saved": ["false", "false"],
                "demog": "1",
                "demofindName": "TEST, PATIENT",
                "activeOnly": "true",
                "demographicKeyword": ["TEST, PATIENT 1961-12-23 (AC)"],
                "provi": "999998",
                "flagproviders": "999998",
                "save": ["Save", "Save & Next"]
            }

            response = self.session.post(url, data=payload)

            if response.status_code == 200:
                print("Request successful!")
                print("Response content:", response.text)
                url = f"{self.base_url}/dms/inboxManage.do"
                payload = {
                    "docid": "18",
                    "method": "updateDocStatusInQueue"
                }

                response = self.session.post(url, data=payload)

                if response.status_code == 200:
                    print("Request successful!")
                    print("Response content:", response.text)
                else:
                    print("Request failed with status code:", response.status_code)
            else:
                print("Request failed with status code:", response.status_code)
