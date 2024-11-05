from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_document_processor_type(self):
	system_type = self.config.get('aimoa_document_processor.type')

	if system_type == 'o19':
		return True

	return False


def check_lock(self):
	if self.config.get('lock.status'):
		self.logger.info(f"Lock already set.")
		return True
	else:
		self.config.update_lock_status(True)
		self.logger.info(f"Lock set.")
		return False

def release_lock(self):
	self.config.update_lock_status(False)
	self.logger.info(f"Lock released.")
	return True

def get_o19_documents(self):
	system_type = self.config.get('emr.document_folder')

	if system_type == 'pending':
		return self.get_inbox_pendingdocs_documents(self)
	elif system_type == 'incoming':
		return self.get_inbox_incomingdocs_documents(self)


def get_inbox_pendingdocs_documents(self):
	driver = self.get_driver(self)
	if driver is not False:
		driver.get(f"{self.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
		script_value = driver.execute_script("return typeDocLab;")
		pending_file = self.config.get('inbox.pending')
		if pending_file is not None:
		    last_processed_file = int(pending_file)
		else:
		    # Handle the case where the key is not set
		    last_processed_file = 0
		for item in script_value['DOC']:
			item = int(item)
			if(item > last_processed_file):
				self.file_name = item
				file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={item}"
				file_response = self.session.get(file_url)

				if file_response.status_code == 200 and file_response.content:
					self.config.set_shared_state('current_file', file_response.content)
					return True
				else:
					self.logger.error(f"An error occurred: {file_response.status_code}")

	return False


def get_inbox_incomingdocs_documents(self):
	driver = self.get_driver(self)
	if driver is not False:
		queue = self.config.get('emr.incoming_folder_queue')
		folder = self.config.get('emr.incoming_folder')
		driver.get(f"{self.base_url}/dms/incomingDocs.jsp")
		driver.execute_script(f"loadPdf('{queue}', '{folder}');")
		driver.implicitly_wait(10)
		select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

		update_time = ""

		for option in select_element.options:
			if(option.get_attribute('value') != ""):
				split_string = option.get_attribute('text').split(") ", 1)

				if(update_time is None or update_time == ""):
					update_time = split_string[1]
				else:
					update_time = self.config.get('inbox.incoming')

				last_file = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
				current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")

				if last_file <= current_file:
					update_time = split_string[1]

					pdf_url = f"{self.base_url}/dms/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir=File&queueId=1&pdfName={option.get_attribute('value')}"
					file_response = self.session.get(pdf_url)

					if file_response.status_code == 200  and file_response.content:
						self.file_name = option.get_attribute('value')
						self.config.set_shared_state('current_file', file_response.content)
						return True
					else:
						self.logger.error(f"An error occurred: {file_response.status_code}")

	return False


def get_driver(self):
	chrome_options = Options()
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
	try:

		if self.login_manager.is_login_successful(self.login_manager.login_with_selenium(driver)):
			return driver
		else:
			return False

	except Exception as e:
		# Handle the exception (log it, re-raise, return None, etc.)
		self.logger.error(f"An error occurred: {e}")
		return False
