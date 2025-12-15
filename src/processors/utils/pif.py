# COPYRIGHT © 2025 by Spring Health Corporation <office(at)springhealth.org>
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

import re
from datetime import datetime
from bs4 import BeautifulSoup
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
import time

def get_postal_code_category(self, postal_code):
    """
    Check the category (primary_fsa or secondary_fsa) based on the postal code prefix.

    :param postal_code: The postal code to check (string).
    :return: "primary_fsa" if postal code matches primary_fsa prefixes, 
             "secondary_fsa" if postal code matches secondary_fsa prefixes, 
             "Unknown" if it doesn't match either category.
    """
    # Define valid prefixes for each category
    self.logger.info("Checking Postal code.")

    primary_fsa_valid_prefixes = self.config.get('pif.primary_fsa_valid_prefixes',['test'])
    secondary_fsa_valid_prefixes = self.config.get('pif.secondary_fsa_valid_prefixes',['test'])
    
    # Normalize the postal code (strip spaces and convert to uppercase)
    postal_code = postal_code.strip().upper()

    # Check for primary_fsa category (if postal code starts with any of the primary_fsa prefixes)
    if any(postal_code.startswith(prefix) for prefix in primary_fsa_valid_prefixes):
        self.logger.info("Postal code under primary_fsa.")
        return "primary_fsa"
    
    # Check for secondary_fsa category (if postal code starts with any of the secondary_fsa prefixes)
    if any(postal_code.startswith(prefix) for prefix in secondary_fsa_valid_prefixes):
        self.logger.info("Postal code under secondary_fsa.")
        return "secondary_fsa"
    
    # If postal code doesn't match any known prefix, return "Not Eligible"
    self.logger.info("Postal code not eligible.")
    return "Not Eligible"


def query_pif(self):
    """
    Processes Patient Intake Forms (PIF) from the database and updates patient details.

    This method queries the configurable table in batches to 
    process PIF records. It fetches records starting from a specified `last_processed_fht_id` 
    and processes them based on a configurable batch size (`pif.batch_size`). For each record, 
    the method checks patient details, verifies them against external databases, and either 
    updates existing patient records or creates new ones if they do not exist. The method also 
    handles cases where specific patient IDs should be skipped and logs all actions.

    The processing involves the following key steps:
    - Fetching a batch of records based on `last_processed_fht_id` and `batch_size`.
    - Checking for valid patient details using either the Health Card Number (HCN) or Date of Birth (DOB).
    - Creating or updating patient demographic information as needed.
    - Creating a tickler (reminder) for patients with invalid status.
    - Skipping records based on a configured list of IDs (`skip_ids`).
    - Logging the progress of each record processed, including any errors.

    Parameters:
        None

    Returns:
        bool: Always returns `True` to indicate successful execution.
        
    Exceptions:
        - If an error occurs during the processing, it logs the error message and creates a tickler for the issue.
    """
    try:

        connection = None
        assigned_to = self.config.get('pif.aimee_uid')
        start_processing = False
        last_processed_fht_id = self.config.get('pif.last_processed', 0)
        starting_fht_id = last_processed_fht_id
        current_row = None
        processed_fht_count = 0
        fht_batch_size = self.config.get('pif.batch_size', 1)
        fht_tickler_id = 0
        skip_ids = []
        start_processing, fht_tickler_id, fht_tickler_data = self.get_fht_tickler_config(self, str(assigned_to))

        if not start_processing:
            return True

        if 'start_from' in fht_tickler_data:
            last_processed_fht_id = fht_tickler_data['start_from']
            starting_fht_id = last_processed_fht_id

        if 'batch_size' in fht_tickler_data:
            fht_batch_size = fht_tickler_data['batch_size']

        if 'skip_ids' in fht_tickler_data:
            skip_ids = fht_tickler_data['skip_ids']

        self.logger.info("Creating connection for PIF.")

        # Establish connection to the MySQL server
        connection = mysql.connector.connect(
            host=self.config.get('pif.host'),
            user=self.config.get('pif.username'),
            password=self.config.get('pif.password'),
            database=self.config.get('pif.database'),
            port=self.config.get('pif.port')
        )

        table_name = self.config.get('pif.table_name')

        # Create a cursor object to interact with the database
        cursor = connection.cursor(dictionary=True)

        sql_query = f"""
            SELECT t.*
            FROM {table_name} t
            JOIN (
                SELECT hcn1, MAX(id) AS max_id
                FROM {table_name}
                WHERE id >= %s
                GROUP BY hcn1
            ) AS latest
            ON t.hcn1 = latest.hcn1 AND t.id = latest.max_id
            ORDER BY t.id ASC
        """

        # Execute the query, passing the value for id
        cursor.execute(sql_query, (last_processed_fht_id,))  # Using a tuple for parameterized query

        # Fetch all results
        results = cursor.fetchall()

        # Print the results
        for row in results:

            if processed_fht_count < fht_batch_size:
                
                last_processed_fht_id = row['id']

                current_row = row

                self.logger.info(f"Started processing PIF Id : {row['id']}")

                if not isinstance(skip_ids, list):
                    if row['id'] == skip_ids:
                        self.logger.info(f"Skipping PIF Id : {row['id']}")
                        processed_fht_count += 1
                        continue

                elif row['id'] in skip_ids:
                    self.logger.info(f"Skipping PIF Id : {row['id']}")
                    processed_fht_count += 1
                    continue

                if row['have_familymd'] in ['No', 'Retire'] and row['lastname1'].lower() != 'test' and row['firstname1'].lower() != 'test':
                    
                    category = self.get_postal_code_category(self, row['postalcode'])

                    if category != "Not Eligible":
                        type_of_query = "search_hin"
                        search_result, data = self.get_patient_Html_Common(self,row['hcn1'],type_of_query)

                        if search_result is False:
                            self.logger.info("Patient not found using HC details, trying DOB.")
                            type_of_query = "search_dob"
                            search_result, data = self.get_patient_Html_Common(self,row['dob1'],type_of_query)
                        else:
                            self.logger.info("Match found using HC details, verifying.")
                            is_patient, patient_id, roster_status, doctor = self.search_patient(self, data, row)

                            if is_patient is False:
                                self.logger.info("Patient not found using HC details, trying DOB.")
                                type_of_query = "search_dob"
                                search_result, data = self.get_patient_Html_Common(self,row['dob1'],type_of_query)
                        
                        if search_result is False:
                            self.logger.info("Patient not found using DOB, Creating new demographic.")
                            self.new_patient_details(self, row, category)
                        else:

                            is_patient, patient_id, roster_status, doctor = self.search_patient(self, data, row)

                            if is_patient is False:
                                patient_id = 0
                                self.logger.info("Patient not in the system, Creating new demographic.")
                                self.new_patient_details(self, row, category)
                            else:
                                skip_providers = self.config.get('pif.exception_provider',['test'])

                                if roster_status == 'TE' or any(x in doctor for x in skip_providers):
                                    message = "From FHT Intake form, double check patient RO status."
                                    to = self.config.get('pif.error_msg_to')
                                    self.create_tickler(self, patient_id, message, to)
                                    self.logger.info("Invalid patient status.")
                                    continue

                                self.logger.info("Patient already in the system, updating details.")
                                self.update_patient_details(self, row, patient_id, category, is_patient)

                self.logger.info(f"Completed processing PIF Id : {row['id']}")

            else:
                break

            processed_fht_count += 1

    except Exception as e:
        # Catch any other unexpected errors
        self.logger.error(f"An unexpected error occurred: {e}")

        if current_row is not None:
            message = f"Error when processing PIF Id : {last_processed_fht_id}; {current_row['lastname1']}, {current_row['firstname1']} ({current_row['dob1']} #{current_row['hcn1']}) "
        else:
            message = f"Error when processing PIF Id : {last_processed_fht_id};"

        to = self.config.get('pif.error_msg_to')
        unattached_patient_id = self.config.get('pif.confidential_unattached_id')
        self.create_tickler(self, str(unattached_patient_id), message, str(to))
    
    finally:
        # Ensure that the connection is closed properly
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            self.logger.info("PIF connection closed.")

        if start_processing:
            self.update_fht_tickler_config(self, fht_tickler_id, processed_fht_count, last_processed_fht_id, starting_fht_id)
            if results:
                self.config.config['pif']['last_processed'] = last_processed_fht_id + 1
                self.config.save_config()

        return True

def update_fht_tickler_config(self, fht_tickler_id, processed_fht_count, last_processed_fht_id, starting_fht_id):
    """
    Updates the control tickler configuration by submitting progress information to the EMR.

    This method updates the control tickler with information about the processing of PIF records. It includes details such as:
    - The starting and last processed PIF ID.
    - The total number of processed PIF records in the current batch.

    The tickler status is also updated to "C" (complete).

    Parameters:
        fht_tickler_id (int): The unique identifier for the tickler to be updated.
        processed_fht_count (int): The number of PIF records processed in the current batch.
        last_processed_fht_id (int): The ID of the last PIF record processed.
        starting_fht_id (int): The ID of the first PIF record processed in the current batch.

    Returns:
        None: This method does not return a value but performs an update on the tickler configuration.
    """
    if self.login_successful:
        self.logger.info("Updating config tickler.")
        driver = self.driver
        driver.execute_script("window.open('');")
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        driver.get(f"{self.base_url}/tickler/ticklerEdit.jsp?tickler_no={fht_tickler_id}")
        driver.implicitly_wait(20)
        message_element = driver.find_element(By.NAME, 'newMessage')
        message_element.send_keys('Starting PIF Id: '+ str(starting_fht_id) +', Processed up to PIF Id : ' + str(last_processed_fht_id) + ', Processed file count : ' + str(processed_fht_count))

        statusSelect = Select(driver.find_element(By.NAME, "status"))
        statusSelect.select_by_value("C")

        driver.execute_script("document.getElementsByName('serviceform')[0].submit();")

        time.sleep(5)

        windows = driver.window_handles
        driver.switch_to.window(windows[-1])

def get_fht_tickler_config(self, assigned_to):
    """
    Retrieves the FHT tickler configuration for a specified user.

    This method fetches the tickler data for a given user (identified by `assigned_to`), and 
    processes the table to extract relevant tickler information. The function then 
    returns a tuple containing:
    - A boolean indicating whether the tickler was found.
    - The tickler ID.
    - A dictionary containing the tickler data.

    If the tickler data includes a 'start' key with the value 'pif', the method returns 
    the tickler ID and its associated data. If no valid tickler is found, it returns 
    `False`, `0`, and `0`.

    Parameters:
        assigned_to (str): The user ID to filter the ticklers assigned to that user.

    Returns:
        tuple: A tuple where:
            - A boolean indicating if a valid tickler was found (`True` or `False`).
            - The tickler ID (if found).
            - A dictionary with the tickler data if found, otherwise `0`.
    """

    if self.login_successful:
        current_date = datetime.now()

        formatted_date = current_date.strftime('%Y-%m-%d')

        driver = self.driver
        driver.get(f"{self.base_url}/tickler/ticklerMain.jsp?ticklerview=A&assignedTo={assigned_to}&xml_vdate={formatted_date}&xml_appointment_date={formatted_date}")
        driver.implicitly_wait(10)

        try:
            table = driver.find_element(By.ID, 'ticklersTbl')
            tbody = table.find_element(By.TAG_NAME, 'tbody')
            rows = tbody.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                td = row.find_elements(By.TAG_NAME, 'td')
                checkbox = row.find_element(By.NAME, 'checkbox')
                tickler_id = checkbox.get_attribute("value")

                s = td[9].text.lower()
                s = s.replace(" ", "")

                parts = s.split(';')
                data = {}

                for p in parts:
                    if ':' in p:
                        key, value = p.split(':', 1)
                        
                        if ',' in value:
                            try:
                                data[key] = list(map(int, value.split(',')))
                            except ValueError:
                                data[key] = value.split(',')
                        else:
                            try:
                                data[key] = int(value)
                            except ValueError:
                                data[key] = value
                    else:
                        data[p] = True

                if 'start' in data and data['start'] == 'pif':
                    return True, tickler_id, data

            return False, 0, 0

        except Exception as e:
            return False, 0, 0

def search_patient(self, data, row):
    """
    Searches for a patient in the provided HTML data using the patient's first and last name.

    This method parses the provided HTML data (in the form of a string) using BeautifulSoup to extract patient information 
    from a table. It then compares the first and last name from the provided `row` to the names in the extracted data to 
    find a match. If a match is found, it returns the patient's ID, roster status, and mrp information.

    The method performs the following steps:
    1. Parses the `data` parameter (HTML) to extract patient-related information (name, ID, roster status, mrp).
    2. Searches for the first and last name in the parsed data.
    3. Returns a tuple containing:
       - A boolean indicating if the patient was found (`is_patient`).
       - The patient's ID (`patient_id`).
       - The patient's roster status (`roster_status`).
       - The mrp's name (`mrp`).

    Parameters:
        data (str): The HTML data containing the patient information to be searched.
        row (dict): A dictionary containing the patient's first and last name (keys `'firstname1'` and `'lastname1'`).

    Returns:
        tuple: A tuple `(is_patient, patient_id, roster_status, doctor)`:
            - `is_patient` (bool): Whether a matching patient was found.
            - `patient_id` (int): The ID of the found patient, or `0` if not found.
            - `roster_status` (str): The patient's roster status, or an empty string if not found.
            - `doctor` (str): The name of the doctor associated with the patient, or an empty string if not found.
    """
    is_patient = False
    patient_id = 0
    roster_status = ''
    mrp = ''
    soup = BeautifulSoup(data, "html.parser")

    pairs = []

    for table_row in soup.find_all("tr"):
        name_cell = table_row.find("td", class_="name")
        chart_cell = table_row.find("td", class_="demoIdSearch")
        roster_status_cell = table_row.find("td", class_="rosterStatus")
        mrp_cell = table_row.find("td", class_="doctor")

        if name_cell and chart_cell:
            link = chart_cell.find("a")
            if link:
                pairs.append((
                name_cell.get_text(strip=True),
                link.get_text(strip=True),
                roster_status_cell.get_text(strip=True),
                mrp_cell.get_text(strip=True)
                ))
    if pairs:

        fn = re.escape(row['firstname1'].rstrip())
        ln = re.escape(row['lastname1'].rstrip())

        pattern_fn = re.compile(rf"\b{fn}\b", re.IGNORECASE)
        pattern_ln = re.compile(rf"\b{ln}\b", re.IGNORECASE)

        for item in pairs:
            name_text = item[0].replace(",", " ").strip()

            if pattern_fn.search(name_text) and pattern_ln.search(name_text):
                is_patient = True
                patient_id = item[1]
                roster_status = item[2]
                mrp = item[3]
                break

    return is_patient, patient_id, roster_status, mrp


def new_patient_details(self, row, category):
    """
    Creates a new patient demographic record using the provided details.

    This method creates a new patient demographic record. 
    It fills in various form fields such as the patient's first name, last name, sex, language preferences, 
    date of birth, email, and postal code. The function also handles potential form submission alerts and 
    checks for any errors during the submission. If successful, it proceeds to update the patient's details.

    The following steps are performed:
    1. Navigate to the new patient demographic creation page.
    2. Fill in the patient's details into the form.
    3. Handle any alert messages or errors.
    4. After successful creation, update the patient’s details using the demographic number.

    Parameters:
        row (dict): A dictionary containing the patient's details such as first name, last name, sex, 
                    date of birth, email, postal code, and language preferences.
        category (str): The fsa type of the patient (used for further processing after the patient is created).

    Returns:
        None: This method does not return a value.
    """
    if self.login_successful:
        driver = self.driver
        driver.get(f"{self.base_url}/demographic/demographicaddarecordhtm.jsp")
        driver.implicitly_wait(20)

        self.fill_element(self, driver, 'first_name', row['firstname1'])
        self.fill_element(self, driver, 'last_name', row['lastname1'])

        if row['title1']:
            title = row['title1'].replace(".", "")
            self.fill_element(self, driver, 'selectTitle', title, 'select_text')

        self.fill_element(self, driver, 'sex', row['sex'], 'select_text')

        if row['language'] == 'French':
            self.fill_element(self, driver, 'language', row['language'], 'select_text')

        slanguage = row['item_language'].replace('"', "").replace("[", "").replace("]", "")
        slanguage = [l.strip() for l in slanguage.split(",") if l.strip() != "English"]
        slanguage = slanguage[0] if slanguage else "English"

        if slanguage == 'Other':
            slanguage = "English"

        self.fill_element(self, driver, 'spoken', slanguage, 'select_value')

        # dob_parts = row['dob1'].split('-')
        # dob = f"{dob_parts[2]}-{dob_parts[1]}-{dob_parts[0]}"
        dob = row['dob1']
        self.fill_element(self, driver, 'inputDOB', dob)

        cslegend_element = driver.find_element(By.XPATH, "//div[@id='contactSection']//legend")
        cslegend_element.click()

        self.fill_element(self, driver, 'inputEmail', row['email'])

        postalcode = row['postalcode'].replace(" ", "")
        postalcode = postalcode[:3] + " " + postalcode[3:]
        self.fill_element(self, driver, 'postal', postalcode.upper())


        addbutton_field = driver.find_element(By.ID, "btnAddRecord")
        addbutton_field.click()

        alert_text = None

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()

        except Exception as e:
            print("No alert message, pass one.")
            pass

        if alert_text:
            message = f"Unable to create demographic, please verify details; PIF Id : {row['id']}; {row['lastname1']}, {row['firstname1']} ({row['dob1']} #{row['hcn1']}) "
            to = self.config.get('pif.error_msg_to')
            unattached_patient_id = self.config.get('pif.confidential_unattached_id')
            self.create_tickler(self, str(unattached_patient_id), message, str(to))
            return

        try:
            wait = WebDriverWait(driver, 30)
            form_submit_element = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Go to record"))
            )
        except TimeoutException:
            self.logger.error(f"Error when processing demographic, PIF Id : {row['id']}")
            message = f"Error when processing PIF Id : {row['id']}; {row['lastname1']}, {row['firstname1']} ({row['dob1']} #{row['hcn1']}) "
            to = self.config.get('pif.error_msg_to')
            unattached_patient_id = self.config.get('pif.confidential_unattached_id')
            self.create_tickler(self, str(unattached_patient_id), message, str(to))
            return

        demographic_href = form_submit_element.get_attribute("href")
        query_string = demographic_href.split('?')[1]
        params = query_string.split('&')
        demographic_no = None
        for param in params:
            key, value = param.split('=')
            if key == 'demographic_no':
                demographic_no = value
                break

        self.update_patient_details(self, row, demographic_no, category)

    else:
        self.logger.error("EMR Login Failure : new_patient_details")


def update_patient_details(self, row, demographic_id, category, is_patient=False):
    """
    Updates an new patient's demographic record in the EMR system.

    This method updates the new patient's demographic details such as address, phone numbers, health card number (HCN), and other 
    personal information. It also handles patient-specific updates and manages consent, emergency 
    contact, and healthcare team information.

    The function works in two modes:
    1. Patient Updates: If the patient is already in the system, it updates their details 
       (such as MRP, resident, healthcare team, etc.).
    2. New Patient Updates: If the patient is not in the system, it will fill in additional 
       fields like consent email and emergency contact details etc.

    Parameters:
        row (dict): A dictionary containing the patient's demographic details (e.g., first name, 
                    last name, address, contact info, health card number).
        demographic_id (str): The unique identifier of the patient's demographic record in the EMR system.
        category (str): The category of the patient, either "primary_fsa" or "secondary_fsa", affecting 
                        the updates made to the record.
        is_patient (bool): A flag indicating whether the record is for an existing patient (default is False).

    Returns:
        None
    """
    if self.login_successful:

        driver = self.driver
        driver.get(f"{self.base_url}/demographic/demographiccontrol.jsp?demographic_no={demographic_id}&displaymode=edit&dboperation=search_detail")
        driver.implicitly_wait(20)

        edit_button = driver.find_element(By.ID, "editBtn")
        edit_button.click()

        if not is_patient:

            driver.find_element(By.ID, "consentEmail").click()

            row['newsletter'] = row['newsletter'].replace(" ", "")

            if row['newsletter'] == 'Yes':
                self.fill_element(self, driver, 'news', 'Paper', 'select_value')
            elif row['newsletter'] == 'No':
                self.fill_element(self, driver, 'news', 'Electronic', 'select_value')

            relationship = f"({row['errelationship']})" if row['errelationship'] else ""
            text = f"{row['ercontact']}{relationship}{row['erphone']};{row['comments1']}"
            self.fill_element(self, driver, 'inputNote', text)

            if category == "primary_fsa":

                self.fill_element(self, driver, 'mrp', str(self.config.get('pif.primary_fsa_mrp_id')), 'select_value')

                self.fill_element(self, driver, 'resident', str(self.config.get('pif.primary_fsa_resident_id')), 'select_value')

                self.fill_element(self, driver, 'internalProviderList', str(self.config.get('pif.primary_fsa_program_id')), 'select_value')

                ipl_add_button = driver.find_element(By.ID, "addHealthCareTeamButton")
                ipl_add_button.click()

            elif category == "secondary_fsa":
                self.fill_element(self, driver, 'mrp', str(self.config.get('pif.secondary_fsa_mrp_id')), 'select_value')

            self.fill_element(self, driver, 'addr', row['address'])

            self.fill_element(self, driver, 'city', row['city'])

            self.fill_element(self, driver, 'phone', row['homephone1'])

            self.fill_element(self, driver, 'cell', row['mobilephone1'])

            self.fill_element(self, driver, 'hinBox', row['hcn1'])

            self.fill_element(self, driver, 'verBox', row['versioncode1'])

            updatebutton_field = driver.find_element(By.ID, "updaterecord2")
            updatebutton_field.click()

            alert_text = None

            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert_text = alert.text
                alert.accept()

            except Exception as e:
                print("No alert message, pass two.")
                pass

            if alert_text:
                hcn_input_field = driver.find_element(By.ID, "hinBox")
                driver.execute_script("arguments[0].value = '';", hcn_input_field)
                updatebutton_field.click()

                message = f"HCN validation error, please check that the demographic information is accurate and complete. PIF Id : {row['id']}; {row['lastname1']}, {row['firstname1']} ({row['dob1']} #{row['hcn1']}) "
                to = self.config.get('pif.error_msg_to')
                self.create_tickler(self, demographic_id, message, str(to))

            if category == "secondary_fsa":
                message = self.config.get('pif.secondary_fsa_message')
                to = self.config.get('pif.secondary_fsa_msg_to')
                self.create_tickler(self, demographic_id, message, str(to))

        if is_patient:
            residentSelect = Select(driver.find_element(By.ID, "resident"))
            selected_text = residentSelect.first_selected_option.text

            if not selected_text.strip():
                if category == "primary_fsa":

                    self.fill_element(self, driver, 'mrp', str(self.config.get('pif.primary_fsa_mrp_id')), 'select_value')

                    self.fill_element(self, driver, 'resident', str(self.config.get('pif.primary_fsa_resident_id')), 'select_value')

                    self.fill_element(self, driver, 'internalProviderList', str(self.config.get('pif.primary_fsa_program_id')), 'select_value')

                    ipl_add_button = driver.find_element(By.ID, "addHealthCareTeamButton")
                    ipl_add_button.click()

                    updatebutton_field = driver.find_element(By.ID, "updaterecord2")
                    updatebutton_field.click()

                elif category == "secondary_fsa":
                    message = self.config.get('pif.secondary_fsa_message')
                    to = self.config.get('pif.secondary_fsa_msg_to')
                    self.create_tickler(self, demographic_id, message, str(to))

    else:
        self.logger.error("EMR Login Failure : update_patient_details")

def create_tickler(self, demographic_id, message, to):
    """
    Creates a new tickler entry in the EMR system for a given patient.

    This function sends a POST request to the EMR system to create a tickler message 
    associated with a specific patient's demographic record. The tickler message 
    can be used to notify assigned users or indicate a task that needs to be completed 
    regarding the patient's information.

    Parameters:
        demographic_id (str): The unique identifier of the patient's demographic record.
        message (str): The content of the tickler message to be created.
        to (str): The identifier of the user to whom the tickler message is assigned.

    Returns:
        bool: `True` if the tickler was successfully created, `False` otherwise.
    """
    url = f"{self.base_url}/tickler/dbTicklerAdd.jsp"

    current_date = datetime.now()

    formatted_date = current_date.strftime('%Y-%m-%d')

    params = {
        "parentAjaxId": "true",
        "updateParent": "true",
        "demographic_no": demographic_id,
        "xml_appointment_date": formatted_date,
        "priority": "Normal",
        "site": self.config.get('pif.site_name'),
        "task_assigned_to": to,
        "textarea": message,
        "docType": "null", 
        "docId": "null",
        "user_no": self.config.get('pif.aimee_uid'),
        "writeToEncounter": "false"
    }

    self.headers['Referer'] = url
    self.session.headers.update(self.headers)
    response = self.session.post(url, data=params, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

    if response.status_code == 200:
        self.logger.info(f"Tickler updated.")
        return True

    self.logger.error(f"An error occurred when updating Tickler: {response.status_code}")
    return False

def fill_element(self, driver, locator_id, value, mode="input", timeout=10):
    """
    Fills an input field or selects a dropdown value based on the provided mode.

    This function interacts with an element on a web page (using Selenium WebDriver),
    either by typing a value into an input field or selecting a value from a dropdown.

    Args:
        driver (WebDriver): Selenium WebDriver instance to interact with the browser.
        locator_id (str): The ID of the HTML element to locate.
        value (str): The value to enter into the input field or select from the dropdown.
        mode (str): The mode of interaction. Can be one of:
            - "input" (default): Types the value into an input field.
            - "select_text": Selects the option by visible text in a dropdown.
            - "select_value": Selects the option by its value attribute in a dropdown.
        timeout (int): Maximum time (in seconds) to wait for the element to appear. Default is 10 seconds.

    Raises:
        TimeoutException: If the element is not found within the specified timeout.
        NoSuchElementException: If the element is not found in the DOM.
        Exception: For any unexpected errors during interaction with the element.

    Example:
        # To input text into a field
        fill_element(driver, 'username_field', 'test_user', mode='input')

        # To select an option from a dropdown by visible text
        fill_element(driver, 'dropdown_field', 'Option 1', mode='select_text')

        # To select an option from a dropdown by value
        fill_element(driver, 'dropdown_field', 'option_1_value', mode='select_value')
    """

    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, locator_id))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", element)

        if mode == "input":
            driver.execute_script("arguments[0].value = '';", element)
            element.send_keys(value)

        elif mode == "select_text":
            Select(element).select_by_visible_text(value)

        elif mode == "select_value":
            Select(element).select_by_value(value)

    except TimeoutException:
        print(f"Element '{locator_id}' did not appear within {timeout}s")
    except NoSuchElementException:
        print(f"Element '{locator_id}' not found")
    except Exception as e:
        print(f"Unexpected error on '{locator_id}': {str(e)}")