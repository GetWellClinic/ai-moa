import json

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def save_config(config, filename='config.json'):
    with open(filename, 'w') as file:
        json.dump(config, file, indent=4)
