import datetime
import requests

def query_prompt(self,prompt):
    data = {
        "messages": [
            {
                "role": "user",
                "content": f"Today's Date is : {datetime.datetime.now().date()}\n. {prompt}"
            }
        ],
        "chat_template": self.config.get('llm.chat_template'),
        "model": self.config.get('llm.model'),
        "temperature": self.config.get('llm.temperature'),
        "character": self.config.get('llm.character'),
        "top_p": self.config.get('llm.top_p')
    }
    response = requests.post(self.url, headers=self.headers, json=data, verify=False)
    content_value = response.json()['choices'][0]['message']['content']
    return True, content_value