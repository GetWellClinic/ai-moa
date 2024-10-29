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
        "chat_template": "{{ bos_token }}{% for message in messages %}{% if (message['role'] == 'user') != (loop.index0 % 2 == 0) %}{{ raise_exception('Conversation roles must alternate user/assistant/user/assistant...') }}{% endif %}{% if message['role'] == 'user' %}{{ '[INST] ' + message['content'] + ' [/INST]' }}{% elif message['role'] == 'assistant' %}{{ message['content'] + eos_token}}{% else %}{{ raise_exception('Only user and assistant roles are supported!') }}{% endif %}{% endfor %}",
        "model": "/models/Mistral-7B-Instruct-v0.3.Q4_K_M.gguf",
        "temperature": 0.1,
        "character": "Assistant",
        "top_p": 0.1
    }
    response = requests.post(self.url, headers=self.headers, json=data, verify=False)
    content_value = response.json()['choices'][0]['message']['content']
    # self.logger.info(f"AI Response: {content_value}")
    return True, content_value