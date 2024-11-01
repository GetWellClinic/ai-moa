import re
from bs4 import BeautifulSoup
import itertools

def get_patient_name(self):
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
                return True,str(table)

    return False


def get_patient_dob(self):

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
    if '.' in query:
        query = query.replace('.', '')

    if ',' in query:
        query = query.replace(',', '')

    table = self.get_patient_Html(self,type_of_query,query)

    if table:
        self.config.set_shared_state('type_of_query',type_of_query)
        return True,str(table)
    else:
        return False



def convert_date(self,query):
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
    response = self.session.post(url, data=payload)

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find_all(class_="odd")
    table += soup.find_all(class_="even")

    return table


def filter_results(self):
    type_of_query = self.config.get_shared_state('type_of_query')
    if type_of_query is not None:
        prompt = f"\n{self.ocr_text}.\n" + self.ai_prompts.get('get_patient_result_filter', '')
        text = self.query_prompt(self,prompt)[1]
        cleaned_string = text.replace("[", "").replace("]", "")
        self.config.set_shared_state(type_of_query+'filter', cleaned_string)
        return True,cleaned_string
    else:
        return False


def unidentified_patients(self):
    patient = '''{
        "formattedDob": "2010-02-28",
        "formattedName": "self.default_values.get('default_provider_tagging_id', '')",
        "demographicNo": "self.default_values.get('default_provider_tagging_id', '')",
        "providerNo": "self.default_values.get('defaul_unidentified_patient_tagging_name', '')"
    }'''

    self.config.set_shared_state('filter_results', patient)
    return True, patient