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

import re
from bs4 import BeautifulSoup
import itertools
import json

def get_patient_name(self):
    """
    Extracts the patient's full name from the OCR text.

    This method sends a query to an AI model to extract the patient's name from the provided OCR text.
    The method then checks the returned result, processes the name, and formats it into a query that can 
    be used to search for patient information in a database.

    It returns a table of matching patient records, if found, or `False` if no valid name is detected.

    Returns:
        tuple: 
            - `True, str(table)` if a valid patient name is found and a matching table is returned.
            - `False` if no valid name is found or if the query result is invalid.

    Example:
        >>> result = manager.get_patient_name()
        >>> print(result)
        (True, '<html_table>')  # if the patient's name was successfully extracted and matched.
    """
    prompt = f"\n{self.ocr_text}.\n\n" + self.ai_prompts.get('get_patient_name', '')
    text = self.query_prompt(self,prompt)[1]
    query = text.lower()

    type_of_query = "search_name"

    if "False" in query:
        return False

    array_pattern = r'\[.*?\]'
    parts = query.split(':')
    parts = [part.strip() for part in parts]
    if len(parts) > 1:
        query = parts[1]

    pattern = r'\bnot provided\b.*?[.!?]'
    match = re.search(pattern, query)
    if match:
        return False


    pattern = r'\bfull name of the patient\b.*?[.!?]'
    match = re.search(pattern, query)
    if match:
        query = match.group()

    if query:

        query = re.sub(r'([A-Za-z]),([A-Za-z])', r'\1, \2', query)

        query = re.sub(r'[.,]', '', query)
        query = re.sub(r'[-]', ' ', query)

        parts = query.split(' is ')
        if len(parts) > 1:
            name_parts = parts[1].split()
        else:
            name_parts = query.split()

        if len(name_parts) > 5:
            return False

        all_combinations = list(itertools.permutations(name_parts))
        formatted_combinations = [f"%{combo[0][:4]}%,%{combo[1][:5]}%" 
                                for combo in all_combinations 
                                if len(combo) > 1 and len(combo[0]) >= 2 and len(combo[1]) >= 3]

        # Initialize an empty string to store all the table results
        all_tables = ""

        for combo in formatted_combinations:
            table = self.get_patient_Html(self,type_of_query,combo)

            if table:
                all_tables += str(table)


        if all_tables:
            self.config.set_shared_state('type_of_query',type_of_query)
            self.config.set_shared_state('type_of_query_table',all_tables)
            return True,all_tables
    
    return False


def get_patient_dob(self):
    """
    Extracts the patient's date of birth (DOB) from the OCR text.

    This method sends a query to an AI model to extract the patient's date of birth from the OCR text.
    The method supports multiple date formats (e.g., "YYYY-MM-DD" and "Month day, year") and converts
    them into a consistent format (YYYY-MM-DD). It then queries the patient data and returns the result.

    Returns:
        str: A formatted HTML table if a valid DOB is found and matched; `False` otherwise.

    Example:
        >>> result = manager.get_patient_dob()
        >>> print(result)
        (True, '<html_table>')  # if the patient's date of birth was successfully extracted and matched.
    """
    prompt = f"\n{self.ocr_text}.\n\n" + self.ai_prompts.get('get_patient_dob', '')
    text = self.query_prompt(self,prompt)[1]
    query = text.lower()

    type_of_query = "search_dob"

    formatted_dates = self.convert_date(self,query)

    if isinstance(formatted_dates, bool) and formatted_dates is False:
        return False
    
    responses = []

    for date in formatted_dates:
        result, table = self.get_patient_Html_Common(self,date,type_of_query)
        if result:
            responses.append(table)

    if responses:
        response_str = "\n".join(responses)
        self.config.set_shared_state('type_of_query_table', response_str)
        return True, response_str

    return False



def get_patient_hin(self):
    """
    Extracts the patient's Health Identification Number (HIN) from the OCR text.

    This method sends a query to an AI model to extract the patient's Health Identification Number 
    from the OCR text. It processes the result and formats the query to match the expected format for 
    patient search in the database.

    Returns:
        str: A formatted HTML table if a valid HIN is found and matched; `False` otherwise.

    Example:
        >>> result = manager.get_patient_hin()
        >>> print(result)
        (True, '<html_table>')  # if the patient's HIN was successfully extracted and matched.
    """
    prompt = f"\n{self.ocr_text}.\n\n" + self.ai_prompts.get('get_patient_hin', '')
    text = self.query_prompt(self,prompt)[1]
    query = text.lower()

    type_of_query = "search_hin"

    query = re.sub(r'[#:.,]', ' ', query)
    query = re.sub(r'[-/]', '', query)
    query = re.sub(r'(\d{3,})\s(\d{3,})', r'\1\2', query)
    query = re.sub(r'(\d{3,})\s(\d{3,})', r'\1\2', query)

    pattern = r'\b[A-Za-z]*\d{6,}[A-Za-z]*\b'
    match = re.search(pattern, query)

    if match is None:
        return False

    query = match.group()

    # Remove leading and trailing letters
    query = re.sub(r'^[A-Za-z]+|[A-Za-z]+$', '', query)

    result, data = self.get_patient_Html_Common(self,query,type_of_query)

    if result:
        return True, data
    else:
        n_str = str(query)
        mid_index = len(n_str) // 2
        if mid_index >= 3:
            part1 = f"{int(n_str[:mid_index])}"
            part2 = f"%{int(n_str[mid_index:])}"
            p1_result, p1_data = self.get_patient_Html_Common(self,part1,type_of_query)
            p2_result, p2_data = self.get_patient_Html_Common(self,part2,type_of_query)

            if p1_result or p2_result:
                    return True, f"{p1_data} {p2_data}"

    return False




def get_patient_Html_Common(self, query, type_of_query):
    """
    Helper function to query the patient data and return the matching HTML table.

    This method standardizes the format of the query by removing any punctuation and sends the query
    to `get_patient_Html` to retrieve the matching records from the system.

    Returns:
        tuple: 
            - `True, str(table)` if matching patient records are found.
            - `False` if no matching records are found.

    Example:
        >>> result = manager.get_patient_Html_Common(query, type_of_query)
        >>> print(result)
        (True, '<html_table>')  # if a matching patient record is found
    """
    query = re.sub(r'[.,]', '', query)

    table = self.get_patient_Html(self,type_of_query,query)

    if table:
        self.config.set_shared_state('type_of_query',type_of_query)
        self.config.set_shared_state('type_of_query_table',str(table))
        return True,str(table)
    else:
        return False, ''



def convert_date(self,query):
    """
    Converts a date in the format 'Month day, year' to 'YYYY-MM-DD'.

    This method takes a date in the textual format (e.g., "January 1, 2000") and converts it to a 
    standard format of 'YYYY-MM-DD' (e.g., "2000-01-01").

    Args:
        query (str): The date string to be converted.

    Returns:
        str: The date in 'YYYY-MM-DD' format.

    Example:
        >>> date = manager.convert_date('January 1, 2000')
        >>> print(date)
        '2000-01-01'  # converted date
    """
    # Regex pattern for DD-MM-YYYY
    pattern_dd_mm = r'\b(\d{2})[-/\s](\d{2})[-/\s](\d{4})\b'
    match_dd_mm = re.search(pattern_dd_mm, query)

    pattern_yyyy = r'\b(\d{4})[-/\s](\d{2})[-/\s](\d{2})\b'
    match_yyyy = re.search(pattern_yyyy, query)

    patternText = r'\b(?:[Jj]an(?:uary)?|[Ff]eb(?:ruary)?|[Mm]ar(?:ch)?|[Aa]pr(?:il)?|[Mm]ay|[Jj]un(?:e)?|[Jj]ul(?:y)?|[Aa]ug(?:ust)?|[Ss]ep(?:tember)?|[Oo]ct(?:ober)?|[Nn]ov(?:ember)?|[Dd]ec(?:ember)?)[-/\s]\d{1,2}[-/\s,][\s]?\d{4}\b'
    matchText = re.search(patternText, query)

    patternText_YYYY = r'\b\d{4}[-/\s](?:[Jj]an(?:uary)?|[Ff]eb(?:ruary)?|[Mm]ar(?:ch)?|[Aa]pr(?:il)?|[Mm]ay|[Jj]un(?:e)?|[Jj]ul(?:y)?|[Aa]ug(?:ust)?|[Ss]ep(?:tember)?|[Oo]ct(?:ober)?|[Nn]ov(?:ember)?|[Dd]ec(?:ember)?)[-/\s,][\s]?\d{1,2}\b'
    matchText_YYYY = re.search(patternText_YYYY, query)

    # Create a mapping for month names to numbers
    months = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12",
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
        "Nov": "11", "Dec": "12"
    }

    month = None
    day = None
    year = None

    if match_dd_mm:
        query = match_dd_mm.group()
        query = re.sub(r'[-/\s]', ' ', query)
        day, month, year = query.split()
    elif match_yyyy:
        query = match_yyyy.group()
        query = re.sub(r'[-/\s]', ' ', query)
        year, month, day = query.split()
    elif matchText:
        query = matchText.group()
        query = re.sub(r'[-/\s]', ' ', query)
        query = re.sub(r'[,]', '', query)
        month, day, year = query.split()
        month = months.get(month.capitalize(), None)
    elif matchText_YYYY:
        query = matchText_YYYY.group()
        query = re.sub(r'[-/\s]', ' ', query)
        year, month, day = query.split()
        month = months.get(month.capitalize(), None)
    else:
        return False

    return [f"{year}-{int(month):02d}-{int(day):02d}", f"{year}-{int(day):02d}-{int(month):02d}"]

def get_mrp_details(self):
    """
    Retrieves and updates the MRP details for the provider based on the 'formattedName'.
    
    This method sends a POST request to the demographic search API with the provided 
    'formattedName', retrieves the provider details, and updates the shared state with 
    the provider number if a matching formatted name is found.

    Args:
        self: The instance of the class.

    Returns:
        tuple: A tuple containing:
            bool: True if the operation succeeded, False otherwise.
            str: The updated data in JSON format.

    Raises:
        JSONDecodeError: If there's an issue decoding the JSON data.
    
    Notes:
        The method expects the 'filter_results' state to contain a JSON string with 
        a key 'formattedName' which will be used to search for provider details.
    """
    data = self.config.get_shared_state('filter_results')[1]

    try:
        data = json.loads(data)
    except json.JSONDecodeError as e:
        self.logger.error(f"JSON decoding error: {e}")
        return False

    formatted_name = data.get('formattedName', '')

    url = f"{self.base_url}/demographic/SearchDemographic.do"

    # Define the payload data
    payload = {
                  "query": formatted_name
                }

    self.headers['Referer'] = url
    self.session.headers.update(self.headers)

    # Send the POST request
    response = self.session.post(url, data=payload, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

    if response.status_code == 200:
        try:
            loaded_data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decoding error: {e}")
            return False

        if loaded_data['results'] and formatted_name.lower() == loaded_data["results"][0]['formattedName'].lower():
            data['providerNo'] = loaded_data["results"][0]['providerNo']
            self.config.set_shared_state('filter_results', (True, json.dumps(data)))

        return True, json.dumps(data)
    else:
        return False

def remove_mrp_details(self):
    """
    Removes MRP details from the 'filter_results' shared state by decoding, modifying, 
    and re-encoding the data.

    This method retrieves the second item from the 'filter_results' shared state, attempts 
    to decode it as JSON, and logs any JSON decoding errors. The 'providerNo' key in the 
    decoded data is updated with the value "_". The modified data is then re-encoded to a 
    JSON string and stored back in the shared state.

    Returns:
        bool: True if the operation is successful, False if there is a JSON decoding error.

    Raises:
        json.JSONDecodeError: If the data cannot be decoded as JSON, an error is logged, 
        and False is returned.
    """
    filter_results = self.config.get_shared_state('filter_results')

    # Check if 'filter_results' exists and has at least two elements
    if filter_results is None or len(filter_results) < 2:
        self.logger.error("'filter_results' is missing or has insufficient data.")
        return False

    data = filter_results[1]

    try:
        data = json.loads(data)
    except json.JSONDecodeError as e:
        self.logger.error(f"JSON decoding error: {e}")
        return False

    data['providerNo'] = "_"
    self.config.set_shared_state('filter_results', (True, json.dumps(data)))
    self.logger.info("Removed MRP info from data.")

    return True


def get_patient_Html(self,type_of_query,query):
    """
    Retrieves patient records from the system based on the search query.

    This method constructs a search payload and sends it via a POST request to the system. It uses the 
    provided query (such as patient name, DOB, or HIN) to search the demographic database and retrieve 
    matching patient records.

    Args:
        type_of_query (str): The type of search query (e.g., "search_name", "search_dob").
        query (str): The query string used to search for the patient.

    Returns:
        list: A list of matching HTML tables with patient data.

    Example:
        >>> table = manager.get_patient_Html('search_name', 'John Doe')
        >>> print(table)
        [<html_table>]  # list of matching patient records
    """
    url = f"{self.base_url}/demographic/demographiccontrol.jsp"

    if type_of_query != "search_demographic_no":
        query = f"%{query}%"

    # Define the payload data
    payload = {
                  "search_mode": type_of_query,
                  "keyword": query,
                  "orderby": ["last_name", "first_name"],
                  "dboperation": "search_titlename",
                  "limit1": 0,
                  "limit2": 10,
                  "displaymode": "Search",
                  "ptstatus": "active",
                  "fromMessenger": "False",
                  "outofdomain": ""
                }

    self.headers['Referer'] = url
    self.session.headers.update(self.headers)

    # Send the POST request
    response = self.session.post(url, data=payload, verify=self.config.get('emr.verify-HTTPS'), timeout=self.config.get('general_setting.timeout', 300))

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find_all(class_="odd") + soup.find_all(class_="even")

    if table:
        return response.text
    else:
        return


def filter_results(self):
    """
    Filters the patient results based on the AI prompt.

    This method sends a filtering query to an AI model and updates the shared state with the filtered 
    results. It cleans the result and stores it in the shared state for further processing.

    Returns:
        tuple: 
            - `True, cleaned_string` if the results are successfully filtered and stored.
            - `False` if no filter result is found.

    Example:
        >>> result = manager.filter_results()
        >>> print(result)
        (True, 'filtered_data')  # cleaned and filtered patient data
    """
    type_of_query = self.config.get_shared_state('type_of_query')
    str_table = self.config.get_shared_state('type_of_query_table')

    soup = BeautifulSoup(str_table, 'html.parser')

    table = soup.find_all(class_="odd") + soup.find_all(class_="even")

    result_table_json = []

    provider_no_pattern = re.compile(r'providerNo=(\d+)')

    for parent in table:

        demo_id = parent.find(class_='demoIdSearch')
        name = parent.find(class_='name')
        dob = parent.find(class_='dob')
        links = parent.find(class_='links')

        data = {}

        if demo_id:
            a_tag = demo_id.find('a')
            if a_tag:
                data['demographicNo'] = a_tag.get_text(strip=True)

        if links:
            a_tag = links.find('a')
            if a_tag:
                onclick_value = a_tag.get('onclick')
                if onclick_value:
                    match = provider_no_pattern.search(onclick_value)
                    if match:
                        provider_no = match.group(1)
                        data['providerNo'] = provider_no

        if name:
            data['formattedName'] = name.get_text(strip=True)

        if dob:
            data['formattedDob'] = dob.get_text(strip=True)

        result, matched_data = self.compare_name_with_text(self,data,self.ocr_text)

        if result:
            result_table_json.append(data)

    table = json.dumps(result_table_json)

    if len(result_table_json) == 1:
        text = str(result_table_json[0]).replace("'", '"')
        self.config.set_shared_state(type_of_query+'filter', text)
        return True,text

    if type_of_query is not None and result_table_json:

        prompt = f"\n{table}.\n{self.ocr_text}.\n\n" + self.ai_prompts.get('get_patient_result_filter', '')
        
        result = self.query_prompt(self, prompt)
        
        if isinstance(result, bool):
            return False

        text = result[1]

        match = re.search(r'```json\n(.*?)```', text, re.DOTALL)

        if match:
            text = match.group(1)

        text = text.replace("'", '"')

        data = json.loads(text)

        matched_data_array = []

        if isinstance(data, list) and len(data) > 1:

            for item in data:
                result, matched_data = self.compare_name_with_text(self,item,self.ocr_text)
                if result:
                    matched_data_array.append(matched_data)

            if len(matched_data_array) > 1:
                result_matched_data_array = ', '.join(matched_data_array)
                prompt = f"\n{result_matched_data_array}.\n{self.ocr_text}.\n\n" + self.ai_prompts.get('get_patient_result_filter', '')
        
                result = self.query_prompt(self, prompt)
                
                if isinstance(result, bool):
                    return False

                text = result[1]

                match = re.search(r'```json\n(.*?)```', text, re.DOTALL)

                if match:
                    text = match.group(1)

            else:
                text = matched_data_array[0]

        json_pattern = r'\{[^{}]*\}'
        json_match = re.search(json_pattern, text)
        if json_match:
            text = json_match.group(0)

        text = text.replace("'", '"')

        self.config.set_shared_state(type_of_query+'filter', text)
        return True,text
    else:
        return False


def unidentified_patients(self):
    """
    Marks the patient as unidentified by assigning default values.

    This method updates the shared state with default values for an unidentified patient, such as 
    name, date of birth, and health identification number. This is useful when the AI system is unable 
    to identify a patient.

    Returns:
        bool: `True` if the patient data is successfully updated with default values.

    Example:
        >>> result = manager.unidentified_patients()
        >>> print(result)
        True  # if the unidentified patient data was successfully set
    """
    if self.file_name == '':
        return False
    patient_data = {
            "formattedDob": self.default_values.get('default_unidentified_patient_tagging_dob', ''),
            "formattedName": self.default_values.get('default_unidentified_patient_tagging_name', ''),
            "demographicNo": self.default_values.get('default_unidentified_patient_tagging_id', ''),
            "providerNo": self.default_values.get('default_unidentified_patient_provider_id', '')
        }
    patient_json = json.dumps(patient_data)
    self.config.set_shared_state('filter_results', (True, patient_json))
    default_error_manager_id = self.default_values.get('default_error_manager_id', None)
    if default_error_manager_id:
        self.config.set_shared_state('error_manager', default_error_manager_id)
    return True

def verify_demographic_number(self):
    """
    Verify if the demographic number exists in the system.

    This method retrieves the demographic number from the shared state, 
    decodes the JSON data, and verifies its existence using `verify_demographic_data`.

    Returns:
        tuple:
            - bool: True if the demographic number is found, False otherwise.
            - str: The demographic number if found, otherwise an empty string.

    Logs:
        - Logs a success message if the demographic number is verified.
        - Logs an error if there is a JSON decoding issue.
        - Logs a message if the demographic number does not exist in the system.
    """
    data = self.decode_json(self, self.config.get_shared_state('filter_results')[1], "verify_demographic_number")

    return False if not data else self.verify_demographic_data(self, data)

def verify_demographic_data(self, data):
    """
    Verify the presence of a patient's demographic data in the system.

    This function extracts demographic details (number, name, and date of birth) from the provided 
    data dictionary and checks if they exist in the patient HTML table retrieved from the system.

    Args:
        data (dict): A dictionary containing patient demographic information with keys:
            - 'demographicNo' (str): The demographic number.
            - 'formattedName' (str): The formatted name.
            - 'formattedDob' (str): The formatted date of birth.

    Returns:
        tuple:
            - (bool): `True` if all demographic details are found in the system, otherwise `False`.
            - (str): The demographic number if found, else an empty string.

    Logs:
        - "Verified demographic number in the system." if all details match.
        - "Demographic number doesn't exist in the system." if any detail is missing.
    """

    # Extract values safely using get()
    demographic_no = data.get('demographicNo', '')
    dob = data.get('formattedDob', '')

    type_of_query = "search_demographic_no"

    table = self.get_patient_Html(self,type_of_query,demographic_no)

    # Compile patterns once
    demographic_pattern = re.compile(rf"\bdemographic_no={demographic_no}&\b")
    dob_pattern = re.compile(rf"<td\s+class=\"dob\"\s*>{re.escape(dob)}</td>")
    name_pattern = r'<td class="name">(.*?)</td>'


    if table:
        has_demographic_no = demographic_pattern.search(str(table))
        has_dob_td = dob_pattern.search(str(table))
        match = re.search(name_pattern, str(table))

        if match:
            text = match.group(1)
        else:
            return False

        text = re.sub(r'[.,]', '', text)
        text = re.sub(r'[-]', ' ', text)

        self.logger.info(f"Comparing LLM response name with demographic search result name.")
        result, matched_data = self.compare_name_with_text(self,data,text)

        if has_demographic_no and has_dob_td and result:
            self.logger.info(f"Verified demographic data with system data.")
            return True
    
    self.logger.info(f"Demographic data doesn't exists or incorrect based on the system.")

    return False



def compare_demographic_results(self):
    """
    Compares the demographic data (DOB, Name, and HIN) to determine if they match.

    This method retrieves the demographic data from the shared state, decodes it, 
    and compares the demographic numbers (demographicNo) across the different data types.
    The function returns `True` if any combination of the data matches, and sets 
    the shared state 'filter_results' with the matching data.

    Returns:
        bool: True if demographic numbers match, False otherwise.
        dict or None: The matching demographic data or None if no match found.
    """
    data_dob = self.config.get_shared_state('search_dobfilter')
    data_name = self.config.get_shared_state('search_namefilter')
    data_hin = self.config.get_shared_state('search_hinfilter')

    data_dob = self.decode_json(self, data_dob, "dob")
    data_name = self.decode_json(self, data_name, "name")
    data_hin = self.decode_json(self, data_hin, "hin")

    self.logger.info("Verifying LLM demographic data (DOB) with system data.")
    if data_dob is not None and not self.verify_demographic_data(self, data_dob):
        data_dob = None

    self.logger.info("Verifying LLM demographic data (Name) with system data.")
    if data_name is not None and not self.verify_demographic_data(self, data_name):
        data_name = None

    self.logger.info("Verifying LLM demographic data (HIN) with system data.")
    if data_hin is not None and not self.verify_demographic_data(self, data_hin):
        data_hin = None


    if not data_dob and not data_name and not data_hin:
        self.logger.info(f"Demographic data not available or invalid.")
        return False

    # Check if all three demographic numbers match
    if data_dob is not None and data_name is not None and data_hin is not None:
        if data_dob.get('demographicNo') == data_name.get('demographicNo') == data_hin.get('demographicNo'):
            self.logger.info("Match (all three) found when comparing demographic number.")
            return True, json.dumps(data_dob)
    
    # Check if two demographic numbers match
    if data_dob is not None and data_name is not None:
        if data_dob.get('demographicNo') == data_name.get('demographicNo'):
            self.config.set_shared_state('filter_results', (True, json.dumps(data_dob)))
            self.logger.info("Match (dob and name) found when comparing filter result demographic number.")
            return True, json.dumps(data_dob)
    
    if data_name is not None and data_hin is not None:
        if data_name.get('demographicNo') == data_hin.get('demographicNo'):
            self.config.set_shared_state('filter_results', (True, json.dumps(data_name)))
            self.logger.info("Match (name and hin) found when comparing filter result demographic number.")
            return True, json.dumps(data_name)
    
    if data_dob is not None and data_hin is not None:
        if data_dob.get('demographicNo') == data_hin.get('demographicNo'):
            self.config.set_shared_state('filter_results', (True, json.dumps(data_dob)))
            self.logger.info("Match (dob and hin) found when comparing filter result demographic number.")
            return True, json.dumps(data_dob)

    if data_hin is not None:
        self.logger.info(f"Comparing LLM response name with document for HIN.")
        result, matched_data = self.compare_name_with_text(self,data_hin,self.ocr_text)
        if result and self.compare_demographic_results_llm(self, data_hin):
            self.config.set_shared_state('filter_results', (result, matched_data))
            return result, matched_data

    if data_dob is not None:
        self.logger.info(f"Comparing LLM response name with document for DOB.")
        result, matched_data = self.compare_name_with_text(self,data_dob,self.ocr_text)
        if result and self.compare_demographic_results_llm(self, data_dob):
            self.config.set_shared_state('filter_results', (result, matched_data))
            return result, matched_data

    if data_name is not None:
        self.logger.info(f"Comparing LLM response name with document for NAME.")
        result, matched_data = self.compare_name_with_text(self,data_name,self.ocr_text)
        if result and self.compare_demographic_results_llm(self, data_name):
            self.config.set_shared_state('filter_results', (result, matched_data))
            return result, matched_data

    return False

def compare_demographic_results_llm(self, data):
    """
    Compares the demographic results from the provided data with the OCR text and
    returns a boolean indicating whether a match was found based on the AI's response.

    The function constructs a prompt by combining the data, predefined LLM prompts, 
    and OCR text, then queries the LLM. If the result contains the word "yes", it 
    is further processed (removing specific punctuation and replacing hyphens with spaces) 
    before being checked against the pattern.

    Args:
        data (str): The data containing demographic information to be compared.

    Returns:
        bool: True if the LLM's response contains the word 'yes' followed by any characters,
              indicating a positive match. False otherwise, or if the result is not a valid boolean.
    """
    prompt = f"\n{self.ocr_text}\n\n" + self.ai_prompts.get('compare_demographic_results_llm', '') + f"\n {data} \n"

    result = self.query_prompt(self, prompt)

    if isinstance(result, bool):
        return False

    query = result[1].lower()

    query = re.sub(r'[.,]', '', query)
    query = re.sub(r'[-]', ' ', query)

    pattern = r'\byes\b.*?'
    match = re.search(pattern, query)

    if match:
        self.logger.info(f"Demographic data verified by LLM and matches the document.")
        return True

    self.logger.info(f"Demographic data verified by LLM and does not match with the document.")
    
    return False

def compare_name_with_text(self, data, text):
    """
    Function to compare the formattedName from the provided data with the OCR text.
    
    Args:
        data (dict): The data dictionary containing 'formattedName'.
    
    Returns:
        tuple: (True, data) if a match is found, (False,) otherwise.
    """
    if data is not None:
        name = data.get('formattedName')  # Get the 'formattedName' from the provided data
        if name:
            name = re.sub(r'[-,]', ' ', name)  # Replace '-' and ',' with spaces
            name = re.sub(r'\s+', ' ', name)   # Normalize multiple spaces to a single space
            name_parts = name.split()          # Split the name into parts
            flag = False

            # Check if all part length
            if all(len(part) <= 3 for part in name_parts):
                # Check if every part except for one in the name_parts has a match in OCR
                missing_parts_count = sum(1 for part in name_parts if not re.search(r'\b' + re.escape(part) + r'\b', text, re.IGNORECASE))

                if missing_parts_count <= 1:
                    flag = True

            else:
                parts_count = 0
                for part in name_parts:
                    if len(part) > 3:  # Only check for parts longer than 3 characters
                        match = re.search(r'\b' + re.escape(part) + r'\b', text, re.IGNORECASE)
                        if match:
                            flag = True
                    if len(part) == 3:
                        match = re.search(r'\b' + re.escape(part) + r'\b', text, re.IGNORECASE)
                        if match:
                            parts_count += 1
                            if parts_count >= 2:
                                year = data.get('formattedDob').split('-')[0]
                                match = re.search(r'\b[-/.]*' + re.escape(year) + r'[-/.]*\b', text, re.IGNORECASE)
                                if match:
                                    flag = True
            
            if flag:
                self.logger.info("Match found when cross checking names.")
                self.config.set_shared_state('filter_results', (True, json.dumps(data)))
                return True, json.dumps(data)  # Return True if match is found, with data
            else:
                self.logger.info("No match found when cross checking names.")
    
    return False, None


def decode_json(self, data, label):
    """
    Attempts to decode a JSON string into a Python object.

    Args:
        data (str): The JSON string to decode.
        label (str): A label used for logging, indicating which data is being processed.

    Returns:
        object or None: Returns the decoded Python object if successful, or None if an error occurs.
        
    Logs:
        If decoding fails, an error is logged with the provided label and error details.
    """
    try:
        if data:
            return json.loads(data)
    except json.JSONDecodeError as e:
        self.logger.info(f"JSON decoding error for {label}: {e}")
    return None