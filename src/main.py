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
from huey.contrib.sqlitedb import SqliteHuey
from huey import crontab
from src.auth import LoginManager, DriverManager, SessionManager
from src.processors.document import DocumentProcessor
from src.processors.pdf import PdfProcessor
from src.processors.workflow import WorkflowProcessor, Workflow
from src.config import ConfigManager
from src.logging import setup_logging

# Initialize Huey with SQLite backend
huey = SqliteHuey('oscar_automation', filename='/app/oscar_tasks.db')

class OscarAutomation:
    def __init__(self, config_file='src/config.yaml'):
        self.config = ConfigManager(config_file, 'src/workflow-config.yaml')
        self.logger = setup_logging(self.config)
        self.session_manager = SessionManager(self.config)
        self.login_manager = LoginManager(self.config)

    def _get_driver(self):
        driver_manager = DriverManager(self.config)
        return driver_manager.get_driver()

    @huey.task()
    def process_pdfs(self):
        pdf_processor = PdfProcessor(self.config, self.session_manager)
        driver = self._get_driver()
        pdf_processor.process_pdfs(
            f"{self.config.get('emr', {}).get('base_url')}/login.do",
            self.login_manager.login_successful_callback
        )
        driver.quit()

    @huey.task()
    def process_documents(self):
        document_processor = DocumentProcessor(self.config, self.session_manager)
        driver = self._get_driver()
        document_processor.process_documents(
            f"{self.config.get('emr', {}).get('base_url')}/login.do",
            self.login_manager.login_successful_callback
        )
        driver.quit()

    @huey.task()
    def process_workflow(self):
        workflow_processor = WorkflowProcessor(self.config, self.session_manager)
        driver = self._get_driver()
        workflow_processor.process_workflow(
            f"{self.config.get('emr', {}).get('base_url')}/login.do",
            self.login_manager.login_successful_callback
        )
        driver.quit()

    @huey.task()
    def process_files(self):
        input_directory = self.config.get('file_processing', {}).get('input_directory')
        allowed_extensions = self.config.get('file_processing', {}).get('allowed_extensions')
        
        for file_name in os.listdir(input_directory):
            if any(file_name.endswith(ext) for ext in allowed_extensions):
                file_path = os.path.join(input_directory, file_name)
                workflow = Workflow(self.config)
                workflow.filepath = file_path
                workflow.file_name = file_name
                workflow.execute_workflow()

@huey.periodic_task(crontab(minute=ConfigManager('src/config.yaml').get('huey.schedule.minute', '*/5')))
def schedule_tasks():
    oscar = OscarAutomation()
    oscar.process_documents()
    oscar.process_pdfs()
    oscar.process_workflow()
    oscar.process_files()

if __name__ == "__main__":
    print("Oscar Automation started. Waiting for scheduled tasks...")
