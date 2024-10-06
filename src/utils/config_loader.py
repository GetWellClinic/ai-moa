import yaml
import os

def load_config(filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def save_config(config, filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
