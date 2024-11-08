

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
    text = self.query_prompt(self,prompt)[1]
    return True, text

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


    return True, self.default_values.get('default_category', '')


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