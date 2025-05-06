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

from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_document_processor_type(self):
	"""
    Determines the document processor type based on the configuration.

    This method checks the system type set in the configuration (`aimoa_document_processor.type`) 
    and returns `True` if the system type is 'emr'. Otherwise, it returns `False`.

    Returns:
        bool: `True` if the system type is 'emr', otherwise `False`.

    Example:
        >>> processor_type = manager.get_document_processor_type()
        >>> print(processor_type)
        True
    """
	system_type = self.config.get('aimoa_document_processor.type')

	return system_type in ['emr']


def check_lock(self):
	"""
    Checks if a lock is already set and, if not, sets the lock.

    This method checks the current lock status in the configuration (`lock.status`).
    If the lock is not set, it updates the status to `True` and logs the action. 
    If the lock is already set, it logs that the lock is in place.

    Returns:
        bool: `True` if the lock is already set, `False` if the lock was successfully set.

    Example:
        >>> lock_status = manager.check_lock()
        >>> print(lock_status)
        True  # if lock is already set
    """
	if self.config.get('lock.status'):
		self.logger.info(f"Lock already set.")
		return True
	else:
		self.config.update_lock_status(True)
		self.logger.info(f"Lock set.")
		return False

def release_lock(self):
	"""
    Releases the current lock.

    This method releases the lock by updating the lock status in the configuration (`lock.status`)
    and logs the action.

    Returns:
        bool: `True` indicating that the lock has been released.

    Example:
        >>> release_status = manager.release_lock()
        >>> print(release_status)
        True  # indicating that lock was released
    """
	self.config.update_lock_status(False)
	self.logger.info(f"Lock released.")
	return True

def get_o19_documents(self):
	"""
    Retrieves documents based on the folder type set in the configuration.

    This method determines the type of document folder (`emr.document_folder`) from the configuration 
    and calls the corresponding method to fetch documents from either the 'pending' or 'incoming' folder.

    Returns:
        bool: `True` if documents were retrieved successfully, `False` otherwise.

    Example:
        >>> documents_fetched = manager.get_o19_documents()
        >>> print(documents_fetched)
        True  # if documents are fetched successfully
    """
	system_type = self.config.get('emr.document_folder')

	if system_type == 'pending':
		system_type = self.config.get('emr.system_type', 'o19')
		verify_document_ids = self.config.get('emr.opro_pendingdocs_ids_auto_increment', False)
		if system_type == 'opro' and verify_document_ids:
			"""
			This is to fix the null status in the 'opro' queue_document_link table.
			It should be removed immediately once the aforementioned issue is resolved.
			"""
			return self.get_inbox_pendingdocs_documents_opro(self)
		else:
			return self.get_inbox_pendingdocs_documents(self)
	elif system_type == 'incoming':
		return self.get_inbox_incomingdocs_documents(self)


def get_inbox_pendingdocs_documents(self):
	"""
    Retrieves documents from the 'pending' folder in the document management system.

    This method uses Selenium WebDriver to access the document management system and 
    fetches documents that are in the 'pending' state based on the script value `typeDocLab`.
    
    It retrieves the content of the next unprocessed document and updates the shared state with it.

    Returns:
        bool: `True` if the document was retrieved successfully, `False` otherwise.

    Example:
        >>> pending_docs_fetched = manager.get_inbox_pendingdocs_documents()
        >>> print(pending_docs_fetched)
        True  # if pending documents are fetched successfully
    """
	if self.login_successful:
		driver = self.driver
		system_type = self.config.get('emr.system_type', 'o19')

		if(system_type == 'openo'):
			driver.get(f"{self.base_url}/documentManager/inboxManage.do?method=getDocumentsInQueues")
		else:
			driver.get(f"{self.base_url}/dms/inboxManage.do?method=getDocumentsInQueues")
		
		try:
			driver.implicitly_wait(115)
			queuenames_field = driver.find_element(By.ID, "queueNames")
		except TimeoutException:
			self.logger.debug("Timeout occurred when loading pending documents.")
			return False
		except NoSuchElementException:
			self.logger.debug("Error occurred when loading pending documents.")
			return False

		script_value = driver.execute_script("return typeDocLab;")
		pending_file = self.config.get('inbox.pending')
		if pending_file is not None:
		    last_processed_file = int(pending_file)
		else:
		    # Handle the case where the key is not set
		    last_processed_file = 0
		for item in script_value['DOC']:
			if not item:
				return False
			item = int(item)
			if(item > last_processed_file):

				max_retries = self.config.get('file_processing.max_retries')  # Get max retry count from configuration
				current_retries = self.config.get('file_processing.pending_retries')  # Get current retry count from configuration

				if max_retries <= current_retries:  # If max retries is equal to current retries
					self.config.update_pending_retries(0)  # Reset the retry count in the configuration
					tag_skipped_files = self.config.get('emr.tag_skipped_files')
					if tag_skipped_files:
						self.file_name = item
					else:
						self.config.update_pending_inbox(item)
						self.logger.info(f"Max retries exceeded for processing. Skipping document No: {item}.")
					return False
				else:
					self.config.update_pending_retries(current_retries + 1)  # Increment the retry count by 1
					self.file_name = item
					file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={item}"
					if(system_type == 'openo'):
						file_url = f"{self.base_url}/documentManager/ManageDocument.do?method=display&doc_no={item}"
					self.headers['Referer'] = file_url
					self.session.headers.update(self.headers)
					file_response = self.session.get(file_url, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

					if file_response.status_code == 200 and file_response.content:
						self.config.set_shared_state('current_file', file_response.content)
						self.logger.info(f"Fetched EMR document from Pending Docs...Processing Document No: {item}.")
						return True
					else:
						self.logger.error(f"An error occurred: {file_response.status_code}")
						return False
	return False


def get_inbox_incomingdocs_documents(self):
	"""
    Retrieves documents from the 'incoming' folder in the document management system.

    This method uses Selenium WebDriver to access the document management system and fetches 
    documents from the 'incoming' queue. It compares timestamps to ensure the latest document is retrieved.

    Returns:
        bool: `True` if the document was retrieved successfully, `False` otherwise.

    Example:
        >>> incoming_docs_fetched = manager.get_inbox_incomingdocs_documents()
        >>> print(incoming_docs_fetched)
        True  # if incoming documents are fetched successfully
    """
	if self.login_successful:
		driver = self.driver
		queue = self.config.get('emr.incoming_folder_queue')
		folder = self.config.get('emr.incoming_folder')
		system_type = self.config.get('emr.system_type', 'o19')

		if(system_type == 'openo'):
			driver.get(f"{self.base_url}/documentManager/incomingDocs.jsp")
		else:
			driver.get(f"{self.base_url}/dms/incomingDocs.jsp")

		driver.execute_script(f"loadPdf('{queue}', '{folder}');")
		driver.implicitly_wait(10)
		select_element = Select(driver.find_element(By.ID, "SelectPdfList"))

		update_time = self.config.get('inbox.incoming', None)

		for option in select_element.options:
			
			item = option.get_attribute('value')

			if item != "":

				split_string = option.get_attribute('text').split(") ", 1)

				if(update_time is None or update_time == ""):
					# Handle the case where the key is not set
					self.logger.info(f"Incoming documents last processed file details missing in configuration.")
					return False

				last_file = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
				current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")
				update_time = split_string[1]

				if last_file <= current_file:

					max_retries = self.config.get('file_processing.max_retries')  # Get max retry count from configuration
					current_retries = self.config.get('file_processing.incoming_retries')  # Get current retry count from configuration

					if max_retries <= current_retries:  # If max retries is equal to current retries
						self.config.update_incoming_retries(0)  # Reset the retry count in the configuration
						tag_skipped_files = self.config.get('emr.tag_skipped_files')
						if tag_skipped_files:
							self.file_name = option.get_attribute('value')
							self.inbox_incoming_lastfile = update_time
						else:
							current_file_plus_one_second = current_file + timedelta(seconds=1)
							self.config.update_incoming_inbox(str(current_file_plus_one_second))
							self.logger.info(f"Max retries exceeded for processing. Skipping document No: {item}.")
						return False
					else:
						self.config.update_incoming_retries(current_retries + 1)  # Increment the retry count by 1

						pdf_url = f"{self.base_url}/dms/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir={folder}&queueId={queue}&pdfName={option.get_attribute('value')}"
						if(system_type == 'openo'):
							pdf_url = f"{self.base_url}/documentManager/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir={folder}&queueId={queue}&pdfName={option.get_attribute('value')}"
						self.headers['Referer'] = pdf_url
						self.session.headers.update(self.headers)
						file_response = self.session.get(pdf_url, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

						if file_response.status_code == 200  and file_response.content:
							self.file_name = option.get_attribute('value')
							self.inbox_incoming_lastfile = update_time
							self.config.set_shared_state('current_file', file_response.content)
							self.logger.info(f"Fetched EMR document from Incoming Docs...Processing Document No: {item}.")
							return True
						else:
							self.logger.error(f"An error occurred: {file_response.status_code}")
							return False
	return False


def get_inbox_pendingdocs_documents_opro(self):
	"""
    Fetch and process the next pending EMR document from the inbox for opro to resolve null in queue_document_link.

    This method increments the next document number to process based on the last
    processed file recorded in the configuration. It constructs a request to fetch
    the document from the DMS, handles retry logic based
    on configurable limits, and updates the processing state accordingly.

    Returns:
        bool: True if a document was successfully fetched and ready for processing;
              False if no documents are left, if an error occurred, or if the document
              should be skipped after exceeding retry limits.
    """
	pending_file = self.config.get('inbox.pending')
	item = 0
	if pending_file is None:
		self.logger.info("Pending documents last processed file details missing in configuration.")
		return False
	else:
		last_processed_file = int(pending_file)
		item = last_processed_file + 1

	max_retries = self.config.get('file_processing.max_retries')  # Get max retry count from configuration
	current_retries = self.config.get('file_processing.pending_retries')  # Get current retry count from configuration
	
	file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={item}"
	self.headers['Referer'] = file_url
	self.session.headers.update(self.headers)
	file_response = self.session.get(file_url, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

	if file_response.status_code == 200 and file_response.content:
		if max_retries <= current_retries:  # If max retries is equal to current retries
			self.config.update_pending_retries(0)  # Reset the retry count in the configuration
			tag_skipped_files = self.config.get('emr.tag_skipped_files')
			if tag_skipped_files:
				self.file_name = item
			else:
				self.config.update_pending_inbox(item)
				self.logger.info(f"Max retries exceeded for processing. Skipping document No: {item}.")
				return False
		else:
			self.config.update_pending_retries(current_retries + 1)
			self.config.set_shared_state('current_file', file_response.content)
			self.file_name = item
			self.logger.info(f"Fetched EMR document from Pending Docs...Processing Document No: {item}.")
			return True
	else:
		self.logger.info(f"No more documents to process or error while fetching document {item}.")
	return False

