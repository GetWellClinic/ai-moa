

def get_category_type(self):
    prompt = f"\n{self.ocr_text}.\n" + self.ai_prompts.get('category_type_prompt', '')
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

    return False


def get_document_description(self):

    category_name = self.config.get_shared_state('get_category_type')[1]

    # Iterate over document categories
    for item in self.document_categories:
        if isinstance(item, dict) and item.get('name') == category_name:
            previous_response = f"\n{self.ocr_text}.\n"
            for task in item['tasks']:
                prompt = previous_response + task['prompt']
                previous_response = self.query_prompt(self,prompt)[1]
                name = 'get_document_description_' + task['name']
                self.config.set_shared_state(name, previous_response)

            return True, previous_response

    return False