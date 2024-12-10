# COPYRIGHT © 2024 by Spring Health Corporation <office(at)springhealth.org>
# Toronto, Ontario, Canada
# SUMMARY: This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software,
# documentation, and configuration files.
# These programs, documentation, and configuration files are made available to you as open source
# in the hopes that your clinic or organization may find it useful and improve your care to the public
# by reducing administrative burden for your staff and service providers.
# NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
# and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
# LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
# Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.
# ***
# NOTICE: We hope that you will consider contributing to our common source code repository so that
# others may benefit from your shared work.
# However, if you distribute this code or serve this application to users in modified form,
# or as part of a derivative work, you are required to make your modified or derivative work
# source code available under the same herein described license.
# Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work
# source code can be acquired publicly in its latest most up-to-date version, within one month.
# ***

import yaml
import os
from filelock import FileLock
from typing import Dict, Any, List

class ConfigManager:
    """
    Manages configuration and workflow configuration for the application.

    This class is responsible for loading, saving, and accessing configuration data 
    from two YAML files: one for general configuration (`config.yaml`) and one for 
    workflow-specific settings (`workflow-config.yaml`). It also supports in-memory 
    storage for temporary data and shared state between different parts of the application.

    Attributes:
        base_dir (str): The base directory where the config files are located.
        config_file (str): Path to the general configuration file.
        workflow_config_file (str): Path to the workflow configuration file.
        config (dict): The loaded general configuration data.
        workflow_config (dict): The loaded workflow configuration data.
        in_memory_storage (dict): Temporary in-memory storage for data.
        shared_state (dict): Shared state across different components of the application.
    """
    def __init__(self, config_file='config.yaml', workflow_config_file='workflow-config.yaml'):
        """
        Initializes the ConfigManager with paths to configuration files.

        Args:
            config_file (str): The path to the general configuration file. Defaults to 'config.yaml'.
            workflow_config_file (str): The path to the workflow configuration file. Defaults to 'workflow-config.yaml'.
        """
        self.base_dir = os.path.dirname(os.path.abspath(__file__)) #Base directory location
        self.config_file = os.path.join(self.base_dir, config_file) #Configurations or settings for the application
        self.workflow_config_file = os.path.join(self.base_dir, workflow_config_file) #Workflow settings for the current workflow
        self.config = self.load_config(self.config_file)
        self.workflow_config = self.load_config(self.workflow_config_file)
        self.in_memory_storage = {} #In memory storage variable
        self.shared_state = {} #Shared state for the application

    def save_workflow_config(self) -> None:
        """
        Saves the current workflow configuration to the workflow config file.

        This method writes the `workflow_config` attribute back to the `workflow-config.yaml` file.

        Raises:
            IOError: If the file cannot be written to.
        """
        with open(self.workflow_config_file, 'w') as file:
            yaml.dump(self.workflow_config, file)


    def save_config(self) -> None:
        """
        Saves the current general configuration to the main config file.

        This method acquires a lock to prevent concurrent writes and then saves the `config` 
        attribute back to the `config.yaml` file.

        Raises:
            IOError: If the file cannot be written to.
        """
        lock = FileLock(f"{self.config_file}.lock")
        with lock:
            with open(self.config_file, 'w') as file:
                yaml.dump(self.config, file)

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """
        Loads a configuration file into a Python dictionary.

        Args:
            file_path (str): The path to the YAML configuration file to be loaded.

        Returns:
            dict: The loaded configuration data.

        Raises:
            FileNotFoundError: If the file does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        lock = FileLock(f"{file_path}.lock")
        with lock:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)

    def reload_config(self) -> None:
        """
        Reloads the configuration file and updates the internal configuration.

        This method loads the configuration file specified in `self.config_file`
        and updates the instance variable `self.config` with the new settings.

        It calls the `load_config` method to perform the actual loading of the
        configuration from the file.

        Attributes:
            config_file (str): The path to the configuration file.
            config (dict): The loaded configuration data.

        Returns:
            None
        """
        self.config = self.load_config(self.config_file)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a value from the general configuration using a dotted key path.

        Args:
            key (str): The dotted key path to retrieve (e.g., 'section.subsection.key').
            default (Any): The default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value from the configuration, or the default value if the key is not found.
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_workflow(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a value from the workflow configuration using a dotted key path.

        Args:
            key (str): The dotted key path to retrieve (e.g., 'workflow.steps').
            default (Any): The default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value from the workflow configuration, or the default value if the key is not found.
        """
        keys = key.split('.')
        value = self.workflow_config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def update_lock_status(self, status: bool) -> None:
        """
        Updates the lock status in the general configuration.

        Args:
            status (bool): The lock status to set (True for locked, False for unlocked).
        """
        self.config['lock']['status'] = status
        self.save_config()

    def update_pending_inbox(self, file_name: str) -> None:
        """
        Updates the 'pending' inbox file name in the general configuration.

        Args:
            file_name (str): The name of the file to set as 'pending' in the inbox.
        """
        self.config['inbox']['pending'] = file_name
        self.save_config()

    def update_incoming_inbox(self, file_name: str) -> None:
        """
        Updates the 'incoming' inbox file name in the general configuration.

        Args:
            file_name (str): The name of the file to set as 'incoming' in the inbox.
        """
        self.config['inbox']['incoming'] = file_name
        self.save_config()

    def update_pending_retries(self, times: int) -> None:
        """
        Update the pending retry count for file processing.

        This method updates the number of pending retries for file processing in the
        configuration and saves the updated configuration to persistent storage.

        Args:
            times (int): The new count of pending retries to set in the configuration.

        Returns:
            None
        """
        self.config['file_processing']['pending_retries'] = times
        self.save_config()

    def update_incoming_retries(self, times: int) -> None:
        """
        Update the incoming retry count for file processing.

        This method updates the number of incoming retries for file processing in the
        configuration and saves the updated configuration to persistent storage.

        Args:
            times (int): The new count of incoming retries to set in the configuration.

        Returns:
            None
        """
        self.config['file_processing']['incoming_retries'] = times
        self.save_config()

    @property
    def workflow_steps(self) -> List[Dict[str, Any]]:
        """
        Retrieves the list of workflow steps from the workflow configuration.

        Returns:
            List[Dict[str, Any]]: The list of workflow steps.
        """
        return self.get_workflow('workflow.steps', [])

    @property
    def document_categories(self) -> List[str]:
        """
        Retrieves the list of document categories from the workflow configuration.

        Returns:
            List[str]: The list of document categories.
        """
        return self.get_workflow('document_categories', [])

    @property
    def ai_prompts(self) -> Dict[str, str]:
        """
        Retrieves the AI prompts from the workflow configuration.

        Returns:
            Dict[str, str]: A dictionary of AI prompts.
        """
        return self.get_workflow('ai_prompts', {})

    @property
    def default_values(self) -> Dict[str, str]:
        """
        Retrieves the default values from the workflow configuration.

        Returns:
            Dict[str, str]: A dictionary of default values.
        """
        return self.get_workflow('default_values', {})

    def set_in_memory(self, key, value):
        """
        Sets a value in in-memory storage.

        Args:
            key (str): The key for the value to store.
            value (Any): The value to store.
        """
        self.in_memory_storage[key] = value

    def get_in_memory(self, key, default=None):
        """
        Retrieves a value from in-memory storage.

        Args:
            key (str): The key of the value to retrieve.
            default (Any): The default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value from in-memory storage, or the default value if not found.
        """
        return self.in_memory_storage.get(key, default)

    def set_shared_state(self, key, value):
        """
        Sets a value in the shared state.

        Args:
            key (str): The key for the shared state value.
            value (Any): The value to store in shared state.
        """
        self.shared_state[key] = value

    def get_shared_state(self, key, default=None):
        """
        Retrieves a value from the shared state.

        Args:
            key (str): The key of the value to retrieve.
            default (Any): The default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value from the shared state, or the default value if not found.
        """
        return self.shared_state.get(key, default)

    def clear_shared_state(self):
        """
        Clears all values from the shared state.
        """
        self.shared_state.clear()
