import logging
from utils.workflow import Workflow

class WorkflowProcessor:
    def __init__(self, config, session_manager):
        self.config = config
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)

    def process_workflow(self, driver, login_url, login_successful_callback):
        self.logger.info("Starting workflow processing")
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.config.base_url}/login.do":
            self.logger.error("Login failed.")
            return

        workflow = Workflow(
            self.config.workflow_file_path,
            self.session_manager.get_session(),
            self.config.base_url,
            "workflow.csv",
            self.config.enable_ocr_gpu
        )
        workflow.execute_tasks_from_csv()
        self.logger.info("Workflow processing completed")
