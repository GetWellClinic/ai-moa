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

def get_category_types(self):
    """
    Retrieves the category types by querying an AI model with a predefined prompt.

    This method constructs a prompt using the OCR text and a specific AI prompt related to category types, then
    queries the AI model for a response.

    Returns:
        tuple: A tuple containing:
            - bool: `True` if the query was successful.
            - str: The text response from the AI model.

    Example:
        >>> result, response = manager.get_category_types()
        >>> print(result, response)
    """
    prompt = f"\n{self.ocr_text}.\n" + self.ai_prompts.get('category_types_prompt', '')
    return self.query_prompt(self,prompt)

def get_category_type(self):
    """
    Retrieves the category type based on the OCR document content.

    This method constructs a prompt using the OCR text and a specific AI prompt related to category type, then
    queries the AI model for a response. It matches the AI model's response with the available document categories
    to find a corresponding category name.

    If a category name is found in the AI model's response, it is returned.

    Returns:
        tuple: A tuple containing:
            - bool: `True` if a matching category was found.
            - str: The matched category name.

    Example:
        >>> result, category = manager.get_category_type()
        >>> print(result, category)
    """
    prompt = f"EMR Document content : {self.config.get_shared_state('get_category_types')[1]}.\n" + self.ai_prompts.get('category_type_prompt', '')
    text = self.query_prompt(self,prompt)[1]
    if '.' in text:
        text = text.replace('.', '')

    category_names = []

    for item in self.document_categories:
        category_names.append(item['name'])

    for word in text.split():

        for index, category in enumerate(category_names):

            if '"' in word:
                word = word.replace('"', '')

            if "'" in word:
                word = word.replace("'", "")

            if word.lower() == category.lower():
                return True, category

            if word.lower().startswith(category.lower()):
                return True, category

    return True, self.default_values.get('default_category', '').lower()


def get_document_description(self):
    """
    Retrieves the document description for a given category based on its tasks.

    This method retrieves the category name from the shared state and then iterates over the document categories.
    For the matching category, it queries an AI model for each task's description and updates the shared state
    with the response.

    Returns:
        tuple: A tuple containing:
            - bool: `True` if the description was successfully retrieved.
            - str: The final document description.

    Example:
        >>> result, description = manager.get_document_description()
        >>> print(result, description)
    """
    category_name = self.config.get_shared_state('get_category_type')[1]

    # Iterate over document categories
    for item in self.document_categories:
        if isinstance(item, dict) and item.get('name').strip().lower() == category_name.strip().lower():
            previous_response = f"\n{self.ocr_text}.\n"
            for task in item['tasks']:
                prompt = previous_response + task['prompt']
                previous_response = self.query_prompt(self,prompt)[1]
                name = 'get_document_description_' + task['name']
                self.config.set_shared_state(name, previous_response)

            return True, previous_response

    return False