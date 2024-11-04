import yaml
import os
from filelock import FileLock
from typing import Dict, Any, List

class ConfigManager:
    def __init__(self, config_file='config.yaml', workflow_config_file='workflow-config.yaml'):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.base_dir, config_file)
        self.workflow_config_file = os.path.join(self.base_dir, workflow_config_file)
        self.config = self.load_config(self.config_file)
        self.workflow_config = self.load_config(self.workflow_config_file)
        self.in_memory_storage = {}
        self.shared_state = {}

    def save_workflow_config(self) -> None:
        with open(self.workflow_config_file, 'w') as file:
            yaml.dump(self.workflow_config, file)


    def save_config(self) -> None:
        lock = FileLock(f"{self.config_file}.lock")
        with lock:
            with open(self.config_file, 'w') as file:
                yaml.dump(self.config, file)

    def load_config(self, file_path: str) -> Dict[str, Any]:
        lock = FileLock(f"{file_path}.lock")
        with lock:
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

    def update_lock_status(self, status: bool) -> None:
        self.config['lock']['status'] = status
        self.save_config()

    def update_pending_inbox(self, file_name: str) -> None:
        self.config['inbox']['pending'] = file_name
        self.save_config()

    def update_incoming_inbox(self, file_name: str) -> None:
        self.config['inbox']['incoming'] = file_name
        self.save_config()

    @property
    def workflow_steps(self) -> List[Dict[str, Any]]:
        return self.get_workflow('workflow.steps', [])

    @property
    def document_categories(self) -> List[str]:
        return self.get_workflow('document_categories', [])

    @property
    def ai_prompts(self) -> Dict[str, str]:
        return self.get_workflow('ai_prompts', {})

    @property
    def default_values(self) -> Dict[str, str]:
        return self.get_workflow('default_values', {})

    def set_in_memory(self, key, value):
        self.in_memory_storage[key] = value

    def get_in_memory(self, key, default=None):
        return self.in_memory_storage.get(key, default)

    def set_shared_state(self, key, value):
        self.shared_state[key] = value

    def get_shared_state(self, key, default=None):
        return self.shared_state.get(key, default)

    def clear_shared_state(self):
        self.shared_state.clear()
