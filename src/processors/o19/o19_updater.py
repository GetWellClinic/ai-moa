import datetime
import json

def update_o19(self):
	"""
    Updates the O19 system with the latest document information, including category type, 
    document description, and patient data.

    This method fetches the patient data and category information from the shared state, processes 
    the data (e.g., extracting patient details, provider numbers), and then updates the system 
    accordingly. The method determines whether the system is processing 'pending' or 'incoming' 
    documents and calls the appropriate method to perform the update.

    Returns:
        bool: `True` if the update was successful, `False` if there was an error or missing data.

    Example:
        >>> update_status = manager.update_o19()
        >>> print(update_status)
        True  # if the update is successful
    """
	self.fileType = self.config.get_shared_state('get_category_type')[1].lower()
	self.document_description = self.config.get_shared_state('get_document_description')[1]
	data = self.config.get_shared_state('filter_results')[1]

	try:
	    data = json.loads(data)
	except json.JSONDecodeError as e:
	    self.logger.error(f"JSON decoding error: {e}")
	    return False

	# Extract values safely using get()
	formatted_name = data.get('formattedName', '')
	formatted_dob = data.get('formattedDob', '')
	demographic_number = data.get('demographicNo', '')
	provider_no = data.get('providerNo', None)

	# Check if the required fields are present
	if not formatted_name or not formatted_dob or not demographic_number:
		self.logger.error("Missing required patient information.")
		return False  # Indicate failure due to missing information

    # Assign values to instance variables
	self.patient_name = f"{formatted_name} ({formatted_dob})"
	self.fl_name = formatted_name
	self.demographic_number = demographic_number

	if provider_no is not None:
	    self.mrp = provider_no

	default_provider_id = self.default_values.get('default_provider_tagging_id', '')

	if(default_provider_id != self.config.get_shared_state('get_provider_list')[1]):
		self.provider_number.append(self.config.get_shared_state('get_provider_list')[1])

	self.provider_number.append(default_provider_id)

	for category in self.document_categories:
		if category['name'] == self.fileType:
			try:
				self.provider_number.append(category['default_tagger'])
			except KeyError:
				self.logger.info(f"Category default tagging id not available for type {self.fileType}.")

	system_type = self.config.get('emr.document_folder')

	if system_type == 'pending':
		return self.update_o19_pendingdocs(self)
	else:
		return self.update_o19_incomingdocs(self)

def update_o19_pendingdocs(self):
	"""
    Updates a pending document in the O19 system.

    This method constructs the necessary parameters for a pending document and sends a POST request 
    to the O19 system to update the document information, including the patient demographic details, 
    document description, and providers. After the document update, the method calls another function 
    to record the last processed file.

    Returns:
        bool: `True` if the document update is successful, `False` if there was an error.

    Example:
        >>> status = manager.update_o19_pendingdocs()
        >>> print(status)
        True  # if the document was successfully updated
    """
	url = f"{self.base_url}/dms/ManageDocument.do"

	# Define the parameters for pending doc
	params = {
	    "method": "documentUpdateAjax",
	    "documentId": self.file_name,
	    "docType": self.fileType,
	    "documentDescription": self.document_description,
	    "observationDate": str(datetime.datetime.now().date()),
	    "demog": self.demographic_number,
	    "demofindName": self.fl_name,
	    "demoName": self.fl_name,
	    "demographicKeyword": self.patient_name
	}

	params["flagproviders"] = []

	for value in self.provider_number:
	    params["flagproviders"].append(value)

	response = self.session.post(url, data=params)

	if response.status_code == 200:
		return self.update_o19_last_processed_file(self)

	self.logger.error(f"An error occurred: {response.status_code}")
	return False


def update_o19_incomingdocs(self):
	"""
    Updates an incoming document in the O19 system.

    This method constructs the parameters for an incoming document and sends a POST request 
    to the O19 system to add the document, including patient details, document description, 
    and provider information. After the document update, the method calls another function 
    to record the last processed file.

    Returns:
        bool: `True` if the incoming document update is successful, `False` if there was an error.

    Example:
        >>> status = manager.update_o19_incomingdocs()
        >>> print(status)
        True  # if the incoming document was successfully updated
    """
	url = f"{self.base_url}/dms/ManageDocument.do"

	# Define the parameters for incoming doc
	params = {
	    "method": "addIncomingDocument",
	    "pdfDir": self.config.get('emr.incoming_folder'),
	    "pdfName": self.file_name,
	    "queueId": self.config.get('emr.incoming_folder_queue'),
	    "pdfNo": "1",
	    "queue": "1",
	    "pdfAction": "",
	    "lastdemographic_no": "1",
	    "entryMode": "Fast",
	    "docType": self.fileType,
	    "docClass": "",
	    "docSubClass": "",
	    "documentDescription": self.document_description,
	    "observationDate": str(datetime.datetime.now().date()),
	    "saved": "false",
	    "demog": self.demographic_number,
	    "demographicKeyword": self.patient_name,
	    "provi": self.provider_number[0],
	    "MRPNo": self.mrp,
	    "MRPName": "undefined",
	    "ProvKeyword": "",
	    "flagproviders":self.provider_number[0],
	    "save": "Save & Next"
	}

	params["flagproviders"] = []

	for value in self.provider_number:
	    params["flagproviders"].append(value)

	response = self.session.post(url, data=params)

	if response.status_code == 200:
		return self.update_o19_last_processed_file(self)

	self.logger.error(f"An error occurred: {response.status_code}")
	return False


def update_o19_last_processed_file(self):
	"""
    Updates the record of the last processed file in the O19 system.

    This method records the file that was last processed in the O19 system, either in the 'pending' 
    or 'incoming' folder, and updates the configuration to reflect this. It then saves the updated configuration.

    Returns:
        bool: `True` if the last processed file was successfully recorded.

    Example:
        >>> status = manager.update_o19_last_processed_file()
        >>> print(status)
        True  # if the last processed file was updated
    """
	system_type = self.config.get('emr.document_folder')

	if system_type == 'pending':
		self.config.update_pending_inbox(self.file_name)
	else:
		self.config.update_incoming_inbox(self.file_name)

	self.config.save_config()

	return True