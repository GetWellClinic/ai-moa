import yaml
import os
from typing import Dict, Any, List

class ConfigManager:
    def __init__(self, config_file='config/config.yaml', workflow_config_file='config/workflow-config.yaml'):
        self.config = self.load_config(config_file)
        self.workflow_config = self.load_config(workflow_config_file)
        self.in_memory_storage = {}

    def load_config(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_workflow(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.workflow_config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    @property
    def workflow_steps(self) -> List[Dict[str, Any]]:
        return self.get_workflow('workflow.steps', [])

    @property
    def document_categories(self) -> List[str]:
        return self.get_workflow('document_categories', [])

    @property
    def ai_prompts(self) -> Dict[str, str]:
        return self.get_workflow('ai_prompts', {})

    def set_in_memory(self, key, value):
        self.in_memory_storage[key] = value

    def get_in_memory(self, key, default=None):
        return self.in_memory_storage.get(key, default)
