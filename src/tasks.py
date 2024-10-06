from huey.contrib.djhuey import task
from processors.pdf_processor import PdfProcessor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from processors.document_processor import DocumentProcessor
from processors.workflow import WorkflowProcessor


def _get_driver(config):
    chrome_options = Options()
    if config.get('chrome_options', {}).get('headless', False):
        chrome_options.add_argument("--headless")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )


@task()
def process_pdfs_task(config, session_manager, login):
    with _get_driver(config) as driver:
        pdf_processor = PdfProcessor(config, session_manager)
        config["last_processed_pdf"] = pdf_processor.process_pdfs(
            driver, f"{config['base_url']}/login.do",
            login.login_successful_callback
        )
    return config["last_processed_pdf"]


@task()
def process_documents_task(config, session_manager, login):
    with _get_driver(config) as driver:
        document_processor = DocumentProcessor(config, session_manager)
        config["last_pending_doc_file"] = document_processor.process_documents(
            driver, f"{config['base_url']}/login.do",
            login.login_successful_callback
        )
    return config["last_pending_doc_file"]


@task()
def process_workflow_task(config, session_manager, login):
    workflow_file_path = config.get('workflow_file_path')
    if workflow_file_path:
        with _get_driver(config) as driver:
            workflow_processor = WorkflowProcessor(config, session_manager)
            workflow_processor.process_workflow(
                driver, f"{config['base_url']}/login.do",
                login.login_successful_callback
            )
        return "Workflow processing completed"
    else:
        return ("Workflow file path is not configured. "
                "Skipping workflow processing.")


@task()
def execute_workflow_step(step_name, *args, **kwargs):
    # Implement the logic for executing a specific workflow step
    pass
