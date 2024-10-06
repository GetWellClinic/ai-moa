import yaml

def load_config(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def save_config(config, filename='config/config.yaml'):
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
