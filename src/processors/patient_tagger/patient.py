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
    prompt = f"\n{self.ocr_text}.\n" + self.ai_prompts.get('get_patient_name', '')
    text = self.query_prompt(self,prompt)[1]
    query = text

    type_of_query = "search_name"

    if "False" in query:
        return False

    array_pattern = r'\[.*?\]'
    parts = query.split(':')
    parts = [part.strip() for part in parts]
    if len(parts) > 1:
        query = parts[1]


    pattern = r'\bfull name of the patient\b.*?[.!?]'
    match = re.search(pattern, query)
    if match:
        query = match.group()

    if query:

        if '.' in query:
            query = query.replace('.', '')

        if ',' in query:
            query = query.replace(',', '')

        parts = query.split(' is ')
        if len(parts) > 1:
            name_parts = parts[1].split()
        else:
            name_parts = query.split()

        if len(name_parts) > 5:
            return False

        all_combinations = list(itertools.permutations(name_parts))
        formatted_combinations = [f"%{combo[0]}%,%{'%'.join(combo[1:])}%" for combo in all_combinations]

        for combo in formatted_combinations:
            table = self.get_patient_Html(self,type_of_query,combo)

            if table:
                self.config.set_shared_state('type_of_query',type_of_query)
                self.config.set_shared_state('type_of_query_table',str(table))
                return True,str(table)

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
    prompt = f"\n{self.ocr_text}.\n" + self.ai_prompts.get('get_patient_dob', '')
    text = self.query_prompt(self,prompt)[1]
    query = text

    type_of_query = "search_dob"

    pattern = r'\bdate of birth of the patient\b.*?[.!?]'
    match = re.search(pattern, query)

    if match:
        query = match.group()
        # print(query)

    pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.search(pattern, query)

    patternText = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b'
    matchText = re.search(patternText, query)

    if match:
        query = match.group()
        # print(query)
    elif matchText:
        query = matchText.group()
        query = self.convert_date(self,query)

    return self.get_patient_Html_Common(self,query,type_of_query)



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
    prompt = f"\n{self.ocr_text}.\n" + self.ai_prompts.get('get_patient_hin', '')
    text = self.query_prompt(self,prompt)[1]
    query = text

    type_of_query = "search_hin"

    pattern = r'\b\d{6,}[A-Za-z]*\b'
    match = re.search(pattern, query)
    if match:
        query = match.group()
        query = query[:-2]

    return self.get_patient_Html_Common(self,query,type_of_query)



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
    if '.' in query:
        query = query.replace('.', '')

    if ',' in query:
        query = query.replace(',', '')

    table = self.get_patient_Html(self,type_of_query,query)

    if table:
        self.config.set_shared_state('type_of_query',type_of_query)
        self.config.set_shared_state('type_of_query_table',str(table))
        return True,str(table)
    else:
        return False



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

    # Split the string into components
    month_str, day_str, year_str = query.split()
    day = int(day_str[:-1])  # Remove the comma and convert to integer
    year = int(year_str)  # Convert year to integer

    # Create a mapping for month names to numbers
    months = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }

    # Get the month number from the mapping
    month = months[month_str]

    # Format the date as YYYY-MM-DD
    formatted_date = f"{year}-{month}-{day:02d}"
    
    return formatted_date


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

    # Define the payload data
    payload = {
                  "search_mode": type_of_query,
                  "keyword": "%"+query+"%",
                  "orderby": ["last_name", "first_name"],
                  "dboperation": "search_titlename",
                  "limit1": 0,
                  "limit2": 10,
                  "displaymode": "Search",
                  "ptstatus": "active",
                  "fromMessenger": "False",
                  "outofdomain": ""
                }

    # Send the POST request
    response = self.session.post(url, data=payload, verify=self.config.get('emr.verify-HTTPS'))

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find_all(class_="odd")
    table += soup.find_all(class_="even")

    return table


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
    table = self.config.get_shared_state('type_of_query_table')
    if type_of_query is not None:
        prompt = f"\n{table}.\n{self.ocr_text}.\n" + self.ai_prompts.get('get_patient_result_filter', '')
        text = self.query_prompt(self,prompt)[1]
        match = re.search(r'```json\n(.*?)```', text, re.DOTALL)

        if match:
            text = match.group(1)

        json_pattern = r'\{.*\}'
        json_match = re.search(json_pattern, text)
        if json_match:
            text = json_match.group(0)

        text = text.replace("'", '"')
        cleaned_string = text.replace("[", "").replace("]", "")
        self.config.set_shared_state(type_of_query+'filter', cleaned_string)
        return True,cleaned_string
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
    patient_data = {
            "formattedDob": self.default_values.get('default_unidentified_patient_tagging_dob', ''),
            "formattedName": self.default_values.get('default_unidentified_patient_tagging_name', ''),
            "demographicNo": self.default_values.get('default_unidentified_patient_tagging_id', ''),
            "providerNo": self.default_values.get('default_unidentified_patient_provider_id', '')
        }
    patient_json = json.dumps(patient_data)
    self.config.set_shared_state('filter_results', (True, patient_json))
    return True