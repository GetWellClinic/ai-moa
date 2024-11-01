
def update_o19(self):

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

	# Add provider to all
	self.provider_number.append(127)

	for value in self.provider_number:
	    params["flagproviders"].append(value)

	# print(params)

	response = self.session.post(url, data=params)

	# print(response)

	return True

	#return False