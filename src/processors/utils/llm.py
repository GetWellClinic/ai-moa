import datetime
import requests

def query_prompt(self,prompt):
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON."
            },
            {
                "role": "user",
                "content": f"Today's Date is : {datetime.datetime.now().date()}\n. {prompt}"
            }
        ],
        "mode": "instruct",
        "temperature": 0.1,
        "character": "Assistant",
        "top_p": 0.1
    }
    response = requests.post(self.url, headers=self.headers, json=data)
    content_value = response.json()['choices'][0]['message']['content']
    self.logger.info(f"AI Response: {content_value}")
    return True, content_value