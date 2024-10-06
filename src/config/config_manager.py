import yaml
import logging
from typing import Dict, Any, List

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logging()

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

    def setup_logging(self) -> logging.Logger:
        logging_config = self.get('logging', {})
        logging.basicConfig(
            level=logging_config.get('level', 'INFO'),
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            filename=logging_config.get('filename', 'workflow.log')
        )
        return logging.getLogger(__name__)

    @property
    def workflow_steps(self) -> List[Dict[str, Any]]:
        return self.get('workflow.steps', [])

    @property
    def document_categories(self) -> List[str]:
        return self.get('document_categories', [])

    @property
    def ai_prompts(self) -> Dict[str, str]:
        return self.get('ai_prompts', {})
