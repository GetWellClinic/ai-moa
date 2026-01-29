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

import json
import re

def pif_pdf(self):
    """
    Processes patient information from a PDF text data and tag's the document in EMR.

    This function performs the following steps:
    1. Searches for a specific tag ('#ai-moa') within the text.
    2. If the tag is found, it attempts to parse the following JSON string.
    3. It looks for a matching category in the document categories and assigns a description accordingly.
    4. It then attempts to find a patient using various identifiers (HCN details, DOB).
    5. If a patient is found, tag's document to the patient, else continues as per workflow

    Returns:
        bool: True if a patient is found and the data is processed successfully, otherwise False.

    Raises:
        json.JSONDecodeError: If the JSON string from PDF text cannot be parsed.
    """

    PDF_TAG = self.config.get('pdf_processor.pdf_tag', '#ai-moa')

    if PDF_TAG not in self.ocr_text:
        return False

    matched_categories = data = None

    pattern = rf'{re.escape(PDF_TAG)}\s*(\{{[^}}]*\}})'
    match = re.search(pattern, self.ocr_text)

    if not match:
        self.logger.info("PDF doesn't contain AIMOA tag.")
        return False


    if match:
        json_str = match.group(1)
        json_str = json_str.replace('\n', ' ')
        try:
            row = json.loads(json_str)
        except json.JSONDecodeError as e:
            self.logger.error("JSON parse error:", e)
            return False

        category_names = [item['name'] for item in self.document_categories]
        matched_categories = [cat.lower() for cat in category_names if cat.lower() in row.get("category", "").lower()]

    if matched_categories:
        self.config.set_shared_state('get_category_type', (True,matched_categories[0]))
        description = 'Add default description for category or in json'
        if 'document_description' in row:
            description = row['document_description']
        else:
            for item in self.document_categories:
                if isinstance(item, dict) and item.get('name').lower() == matched_categories[0].lower() and item.get('default_description'):
                    description = item['default_description']
        self.config.set_shared_state('get_document_description', (True, description))

        type_of_query = "search_hin"
        search_result, data = self.get_patient_Html_Common(self,row['hin'],type_of_query)

        is_patient = False

        if search_result is False:
            self.logger.info("Patient not found using HC details, trying DOB.")
            type_of_query = "search_dob"
            search_result, data = self.get_patient_Html_Common(self,row['dob1'],type_of_query)
        else:
            self.logger.info("Match found using HC details, verifying.")
            is_patient, patient_id, roster_status, doctor = self.search_patient(self, data, row, 'hcn')

            if is_patient is False:
                self.logger.info("Patient not found using HC details, trying DOB.")
                type_of_query = "search_dob"
                search_result, data = self.get_patient_Html_Common(self,row['dob1'],type_of_query)

        if search_result is False:
            self.logger.info("Patient not found using DOB, trying with ai-moa.")
            return False
        else:
            if is_patient is False:
                is_patient, patient_id, roster_status, doctor = self.search_patient(self, data, row, 'dob')

            if is_patient is False:
                patient_id = 0
                self.logger.info("Patient not found using DOB, trying with ai-moa")
                return False
            else:
                patient_data = {
                    "formattedDob": row['dob1'],
                    "formattedName": f"{row['lastname1']}, {row['firstname1']}",
                    "demographicNo": patient_id,
                    "providerNo": '_'
                }
                patient_json = json.dumps(patient_data)
                self.config.set_shared_state('filter_results', (True, patient_json))
        
        self.update_o19(self)

        return True

    else:

        return False