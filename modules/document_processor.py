class DocumentProcessor:
    """
    The DocumentProcessor class handles the retrieval and processing of documents from the EMR.
    It provides methods to fetch file content from the server and process documents through automated interactions with a web interface.
    """

    def __init__(self, base_url, session):
        """
        Initializes the DocumentProcessor with the base URL of the EMR server and a session object for making HTTP requests.

        :param base_url: The base URL of the EMR server.
        :param session: A session object for making HTTP requests.
        """
        self.base_url = base_url
        self.session = session

    def get_file_content(self, name):
        """
        Fetches the content of a file from the DMS server.

        :param name: The document number or name used to identify the file.
        :return: The filename if the file is successfully saved, otherwise None.
        """
        # Construct the file URL using the base URL and document name
        file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={name}"
        # Make a GET request to the file URL
        file_response = self.session.get(file_url)
        if file_response.status_code == 200:
            # Retrieve the content type from the response headers
            content_type = file_response.headers.get("content-type")
            # Extract the file extension from the content type
            file_extension = content_type.split("/")[-1] if content_type else "txt"
            # Construct the filename with the appropriate extension
            filename = f"{name}.{file_extension}"
            # Save the file content to a local file
            with open(filename, "wb") as file:
                file.write(file_response.content)
            print("File saved as:", filename)
            return filename
        else:
            # Print an error message if the file content could not be fetched
            print("Failed to fetch file content. Status code:", file_response.status_code)
            return None

    def process_documents(self, driver, login_url, login_successful_callback):
        """
        Processes documents by automating interactions with the web interface using a web driver.

        :param driver: The web driver used for browser automation.
        :param login_url: The URL for the login page.
        :param login_successful_callback: A callback function that checks if the login was successful.
        """
        # Navigate to the login page
        driver.get(login_url)
        # Execute the login successful callback to check if login was successful
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            # Print an error message if login failed
            print("Login failed.")
            return

        # Navigate to the document queue management page
        driver.get(f"{self.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
        # Execute a JavaScript script to retrieve document queue information
        script_value = driver.execute_script("return typeDocLab;")
        print("Script value obtained from the document queue page:", script_value)

        # Fetch the content of a specific document
        filename = self.get_file_content("30")
        if filename:
            # Define the URL for updating the document
            url = f"{self.base_url}/dms/ManageDocument.do"
            # Define the payload for the document update request
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

            # Send a POST request to update the document
            response = self.session.post(url, data=payload)

            if response.status_code == 200:
                print("Document update request successful!")
                print("Response content:", response.text)
                # Define the URL for updating the document status in the queue
                url = f"{self.base_url}/dms/inboxManage.do"
                # Define the payload for the document status update request
                payload = {
                    "docid": "18",
                    "method": "updateDocStatusInQueue"
                }

                # Send a POST request to update the document status in the queue
                response = self.session.post(url, data=payload)

                if response.status_code == 200:
                    print("Document status update request successful!")
                    print("Response content:", response.text)
                else:
                    print("Document status update request failed with status code:", response.status_code)
            else:
                print("Document update request failed with status code:", response.status_code)
