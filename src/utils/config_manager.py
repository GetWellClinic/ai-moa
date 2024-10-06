import os
import yaml
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)

    def save_config(self):
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()

    @property
    def user_login(self) -> Dict[str, str]:
        return self.config['user_login']

    @property
    def base_url(self) -> str:
        return self.config['base_url']

    @property
    def last_processed_pdf(self) -> str:
        return self.config['last_processed_pdf']

    @last_processed_pdf.setter
    def last_processed_pdf(self, value: str):
        self.config['last_processed_pdf'] = value
        self.save_config()

    @property
    def last_pending_doc_file(self) -> str:
        return self.config['last_pending_doc_file']

    @last_pending_doc_file.setter
    def last_pending_doc_file(self, value: str):
        self.config['last_pending_doc_file'] = value
        self.save_config()

    @property
    def enable_ocr_gpu(self) -> bool:
        return self.config['enable_ocr_gpu']

    @property
    def workflow_file_path(self) -> str:
        return self.config.get('workflow_file_path', 'workflow.csv')

    @property
    def chrome_options(self) -> Dict[str, Any]:
        return self.config['chrome_options']
