"""
Copyright (C) 2024 Spring Health Corporation

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Main module for automating Oscar EMR tasks using Huey for task management.
"""

import os
from huey import MemoryHuey
from huey.api import task, TaskLock
from src.auth import LoginManager, DriverManager, SessionManager
from src.processors.document import DocumentProcessor
from src.processors.pdf import PdfProcessor
from src.processors.workflow import WorkflowProcessor, Workflow
from src.config import ConfigManager
from src.logging import setup_logging

class OscarAutomation:
    def __init__(self, config_file='config/workflow-config.yaml'):
        self.config = ConfigManager(config_file)
        self.logger = setup_logging()
        self.session_manager = SessionManager(self.config)
        self.login_manager = LoginManager(self.config)
        self.huey = self.setup_huey()

    def _get_driver(self):
        driver_manager = DriverManager(self.config)
        return driver_manager.get_driver()

    def setup_huey(self):
        huey_config = self.config.get('huey', {})
        return MemoryHuey(
            name=huey_config.get('name', 'workflow_queue'),
            results=huey_config.get('results', True),
            store_none=huey_config.get('store_none', False),
            always_eager=huey_config.get('always_eager', True)
        )

    @task()
    def process_pdfs(self):
        with TaskLock('pdf_processing'):
            pdf_processor = PdfProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            pdf_processor.process_pdfs(
                driver,
                f"{self.config.get('emr', {}).get('base_url')}/login.do",
                self.login_manager.login_successful_callback
            )
            driver.quit()

    @task()
    def process_documents(self):
        with TaskLock('document_processing'):
            document_processor = DocumentProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            document_processor.process_documents(
                driver,
                f"{self.config.get('emr', {}).get('base_url')}/login.do",
                self.login_manager.login_successful_callback
            )
            driver.quit()

    @task()
    def process_workflow(self):
        with TaskLock('workflow_processing'):
            workflow_processor = WorkflowProcessor(self.config, self.session_manager)
            driver = self._get_driver()
            workflow_processor.process_workflow(
                driver,
                f"{self.config.get('emr', {}).get('base_url')}/login.do",
                self.login_manager.login_successful_callback
            )
            driver.quit()

    @task()
    def process_files(self):
        with TaskLock('file_processing'):
            input_directory = self.config.get('file_processing', {}).get('input_directory')
            allowed_extensions = self.config.get('file_processing', {}).get('allowed_extensions')
            
            for file_name in os.listdir(input_directory):
                if any(file_name.endswith(ext) for ext in allowed_extensions):
                    file_path = os.path.join(input_directory, file_name)
                    workflow = Workflow(self.config)
                    workflow.filepath = file_path
                    workflow.file_name = file_name
                    workflow.execute_workflow()

    @task()
    def schedule_tasks(self):
        self.logger.info("Scheduling tasks")
        self.process_documents()
        self.process_pdfs()
        self.process_workflow()
        self.process_files()

import os

def main():
    env = os.environ.get('APP_ENV', 'development')
    config = ConfigManager(env)
    oscar = OscarAutomation(config)
    oscar.schedule_tasks()

if __name__ == "__main__":
    main()
