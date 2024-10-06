import yaml
import os
from typing import Dict, Any, List
from src.utils.logging_setup import setup_logging

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config', config_path)
        self.config = self.load_config()
        self.logger = setup_logging(self)

    def load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as config_file:
            return yaml.safe_load(config_file)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    @property
    def workflow_steps(self) -> List[Dict[str, Any]]:
        return self.get('workflow.steps', [])

    @property
    def document_categories(self) -> List[str]:
        return self.get('document_categories', [])

    @property
    def ai_prompts(self) -> Dict[str, str]:
        return self.get('ai_prompts', {})
