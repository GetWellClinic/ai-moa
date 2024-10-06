import logging
from utils.workflow import Workflow

class WorkflowProcessor:
    def __init__(self, workflow_file, session, base_url, enable_ocr_gpu):
        self.workflow_file = workflow_file
        self.session = session
        self.base_url = base_url
        self.enable_ocr_gpu = enable_ocr_gpu
        self.logger = logging.getLogger(__name__)

    def process_workflow(self, driver, login_url, login_successful_callback):
        self.logger.info("Starting workflow processing")
        driver.get(login_url)
        current_url = login_successful_callback(driver)
        if current_url == f"{self.base_url}/login.do":
            self.logger.error("Login failed.")
            return

        workflow = Workflow(self.workflow_file, self.session, self.base_url, "workflow.csv", self.enable_ocr_gpu)
        workflow.execute_tasks_from_csv()
        self.logger.info("Workflow processing completed")
