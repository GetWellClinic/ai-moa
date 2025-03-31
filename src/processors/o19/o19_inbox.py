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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_document_processor_type(self):
	"""
    Determines the document processor type based on the configuration.

    This method checks the system type set in the configuration (`aimoa_document_processor.type`) 
    and returns `True` if the system type is 'o19'. Otherwise, it returns `False`.

    Returns:
        bool: `True` if the system type is 'o19', otherwise `False`.

    Example:
        >>> processor_type = manager.get_document_processor_type()
        >>> print(processor_type)
        True
    """
	system_type = self.config.get('aimoa_document_processor.type')

	return system_type in ['o19', 'o15']


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
			if not item:
				driver.close()
				driver.quit()
				return False
			item = int(item)
			if(item > last_processed_file):

				max_retries = self.config.get('file_processing.max_retries')  # Get max retry count from configuration
				current_retries = self.config.get('file_processing.pending_retries')  # Get current retry count from configuration

				if max_retries <= current_retries:  # If max retries is equal to current retries
					self.config.update_pending_retries(0)  # Reset the retry count in the configuration
					self.config.update_pending_inbox(item)
					self.logger.info(f"Max retries exceeded for document {item}.")
					driver.close()
					driver.quit()
					return False
				else:
					self.config.update_pending_retries(current_retries + 1)  # Increment the retry count by 1
					self.file_name = item
					file_url = f"{self.base_url}/dms/ManageDocument.do?method=display&doc_no={item}"
					self.get_driver_session(self, driver)
					self.headers['Referer'] = file_url
					self.session.headers.update(self.headers)
					file_response = self.session.get(file_url, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

					if file_response.status_code == 200 and file_response.content:
						self.config.set_shared_state('current_file', file_response.content)
						self.logger.info(f"Fetched EMR document from Pending Docs...Processing Document No: {item}.")
						driver.close()
						driver.quit()
						return True
					else:
						self.logger.error(f"An error occurred: {file_response.status_code}")
						driver.close()
						driver.quit()
						return False
		driver.close()
		driver.quit()
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
	driver = self.get_driver(self)
	if driver is not False:
		queue = self.config.get('emr.incoming_folder_queue')
		folder = self.config.get('emr.incoming_folder')
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
					driver.close()
					driver.quit()
					return False

				last_file = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
				current_file = datetime.strptime(split_string[1], "%Y-%m-%d %H:%M:%S")

				if last_file <= current_file:

					max_retries = self.config.get('file_processing.max_retries')  # Get max retry count from configuration
					current_retries = self.config.get('file_processing.incoming_retries')  # Get current retry count from configuration

					if max_retries <= current_retries:  # If max retries is equal to current retries
						self.config.update_incoming_retries(0)  # Reset the retry count in the configuration
						current_file_plus_one_second = current_file + timedelta(seconds=1)
						self.config.update_incoming_inbox(str(current_file_plus_one_second))
						self.logger.info(f"Max retries exceeded for document {item}.")
						driver.close()
						driver.quit()
						return False
					else:
						self.config.update_incoming_retries(current_retries + 1)  # Increment the retry count by 1

						update_time = split_string[1]

						pdf_url = f"{self.base_url}/dms/ManageDocument.do?method=displayIncomingDocs&curPage=1&pdfDir={folder}&queueId={queue}&pdfName={option.get_attribute('value')}"
						self.get_driver_session(self, driver)
						self.headers['Referer'] = pdf_url
						self.session.headers.update(self.headers)
						file_response = self.session.get(pdf_url, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

						if file_response.status_code == 200  and file_response.content:
							self.file_name = option.get_attribute('value')
							self.inbox_incoming_lastfile = update_time
							self.config.set_shared_state('current_file', file_response.content)
							self.logger.info(f"Fetched EMR document from Incoming Docs...Processing Document No: {item}.")
							driver.close()
							driver.quit()
							return True
						else:
							self.logger.error(f"An error occurred: {file_response.status_code}")
							driver.close()
							driver.quit()
							return False

		driver.close()
		driver.quit()
	return False


def get_driver(self):
	"""
    Retrieves a Selenium WebDriver instance for interaction with the web-based system.

    This method configures Chrome options and creates a Chrome WebDriver instance using 
    the `webdriver_manager` library. It then attempts to log in using Selenium. If login is successful, 
    the driver instance is returned, otherwise, it returns `False`.

    Returns:
        webdriver.Chrome | bool: The WebDriver instance if login is successful, 
        `False` otherwise.

    Example:
        >>> driver = manager.get_driver()
        >>> print(driver)
        <selenium.webdriver.chrome.webdriver.WebDriver object at 0x...>  # if login is successful
    """
	chrome_options = Options()
	if self.config.get('chrome.options.headless', False):
            chrome_options.add_argument("--headless")
            self.logger.debug("Chrome headless mode enabled")
	if not self.config.get('emr.verify-HTTPS', False):
		chrome_options.add_argument('--ignore-certificate-errors')
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
	try:

		if self.login_manager.is_login_successful(self.login_manager.login_with_selenium(driver)):
			return driver
		else:
			driver.close()
			driver.quit()
			return False

	except Exception as e:
		# Handle the exception (log it, re-raise, return None, etc.)
		self.logger.error(f"An error occurred: {e}")
		driver.close()
		driver.quit()
		return False

def get_driver_session(self, driver):
	"""
	Retrieves the session cookies from a Selenium WebDriver and sets them in the current session.

	This method checks the system type specified in the configuration (defaulting to 'o19'). 
	If the system type is either 'opro' or 'opro_pin', it retrieves the cookies from the
	provided Selenium WebDriver instance and sets them in the session's cookie jar.

	Args:
	driver (selenium.webdriver): The Selenium WebDriver instance from which cookies will
	                              be retrieved.

	Returns:
		None: This method does not return anything. It modifies the session's cookies directly.
	"""
	system_type = self.config.get('emr.system_type', 'o19')
	
	if(system_type == 'opro' or system_type == 'opro_pin'):
		cookies = driver.get_cookies()
		for cookie in cookies:
			self.session.cookies.set(cookie['name'], cookie['value'])
