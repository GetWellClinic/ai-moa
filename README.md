# AI-MOA (AI-powered Medical Office Assistant)

AI-MOA is an AI-powered Medical Office Assistant designed to automate various tasks in a medical office setting, particularly focusing on document processing and workflow management within the O19 Electronic Medical Record (EMR) system.

## Project Structure

```
ai-moa/
├── src/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── driver_manager.py
│   │   ├── login_manager.py
│   │   └── session_manager.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   └── provider_list_manager.py
│   ├── logging/
│   │   ├── __init__.py
│   │   └── logging_setup.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── document/
│   │   │   ├── __init__.py
│   │   │   └── document_processor.py
│   │   ├── pdf/
│   │   │   ├── __init__.py
│   │   │   ├── ocr.py
│   │   │   ├── pdf_fetcher.py
│   │   │   └── pdf_processor.py
│   │   └── workflow/
│   │       ├── __init__.py
│   │       ├── emr_workflow.py
│   │       ├── processor.py
│   │       ├── step_executor.py
│   │       └── task_manager.py
│   ├── testing/
│   │   ├── full_workflow_test.py
│   │   └── prompt_testing_script.py
│   ├── config.yaml
│   ├── main.py
│   ├── requirements.txt
│   └── workflow-config.yaml
├── docker-compose.yaml
├── Dockerfile
├── LICENSE
└── README.md
```

## Features

- Automated document processing and classification
- PDF processing with OCR capabilities
- Intelligent workflow management
- Integration with O19 EMR system
- Automated login and session management
- Configurable settings and workflows
- Provider list management
- Extensive error handling and logging
- Docker support for easy deployment
- Task queue management with Huey (in-memory storage)

## How It Works

1. **Initialization**: The `AIMOAAutomation` class in `main.py` initializes the system, loading configurations and setting up logging.
2. **Login**: The `LoginManager` class in `auth/login_manager.py` handles automated login to the O19 EMR system using Selenium WebDriver.
3. **Session Management**: The `SessionManager` class in `auth/session_manager.py` maintains the session for interacting with the O19 EMR system.
4. **Document Processing**: The `DocumentProcessor` class in `processors/document/document_processor.py` handles incoming documents.
5. **PDF Processing**: The `PdfProcessor` class in `processors/pdf/pdf_processor.py` specifically handles PDF documents, including OCR processing.
6. **Workflow Management**: The `WorkflowProcessor` class in `processors/workflow/processor.py` manages the execution of workflows.

## Configuration

The project uses two main configuration files:

1. `src/config.yaml`: Contains general system settings, logging configuration, and file processing options.
2. `src/workflow-config.yaml`: Defines document categories, workflow steps, and AI prompts for document processing.

## AI Integration

- The system uses a local AI model accessed via API (configured in `ai_config` in config.yaml).
- AI prompts are constructed based on the extracted document text and specific tasks.
- The `build_prompt()` and `build_sub_prompt()` methods in the `Workflow` class handle AI interactions.

## O19 EMR Integration

- The system interacts with O19 EMR for patient and provider searches, and document updates.
- The `ProviderListManager` class in `config/provider_list_manager.py` manages provider information.

## Setup and Usage

1. Clone the repository
2. Install dependencies: `pip install -r src/requirements.txt`
3. Configure `src/config.yaml` and `src/workflow-config.yaml`
4. Ensure Chrome WebDriver is installed (for Selenium-based operations)
5. Run the system: `python src/main.py`

Alternatively, you can use Docker:

1. Build the Docker image: `docker build -t ai-moa .`
2. Run the container: `docker-compose up`

## Testing

The `testing` directory contains scripts for testing the full workflow and prompts:

- `full_workflow_test.py`: Tests the entire document processing workflow
- `prompt_testing_script.py`: Tests AI prompts and document classification

## Error Handling and Logging

- Logging is configured in `logging/logging_setup.py`
- Logs are written to both console and file as specified in the configuration

## Contributing

Contributions to improve AI-MOA are welcome. Please follow the standard fork, branch, and pull request workflow. Ensure that your code adheres to the existing style conventions and includes appropriate tests and documentation.

## License

This project is licensed under the GNU Affero General Public License v3.0. See the LICENSE file for details.

## Disclaimer

This software is provided "AS IS" without warranty of any kind. It is intended for use in medical office settings but should be thoroughly tested and validated before use in any critical systems. Ensure compliance with all relevant medical data privacy regulations when using this software.

## Support

For questions, bug reports, or feature requests, please open an issue on the GitHub repository.
