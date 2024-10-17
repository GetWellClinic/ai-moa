

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