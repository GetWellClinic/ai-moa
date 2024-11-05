import datetime
import json

def update_o19(self):

	self.fileType = self.config.get_shared_state('get_category_type')[1]
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
	system_type = self.config.get('emr.document_folder')

	if system_type == 'pending':
		self.config.update_pending_inbox(self.file_name)
	else:
		self.config.update_incoming_inbox(self.file_name)

	self.config.save_config()

	return True