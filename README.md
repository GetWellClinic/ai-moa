# AI-MOA (AI-powered Medical Office Assistant)

This project is an AI-powered Medical Office Assistant designed to automate various tasks in a medical office setting, particularly focusing on document processing and workflow management within the OSCAR Electronic Medical Record (EMR) system.

## Project Structure

```
ai_moa/
├── config/
│   └── config.yaml
├── src/
│   ├── models/
│   │   ├── login.py
│   │   └── session_manager.py
│   ├── processors/
│   │   ├── document_processor.py
│   │   ├── pdf_processor.py
│   │   └── workflow_processor.py
│   ├── utils/
│   │   ├── config_loader.py
│   │   ├── config_manager.py
│   │   ├── logging_setup.py
│   │   ├── ocr_utils.py
│   │   ├── OscarProviderList.py
│   │   ├── tesseract.py
│   │   └── workflow.py
│   ├── workflows/
│   │   ├── 0.csv
│   │   ├── 1.csv
│   │   └── ...
│   └── main.py
├── LICENSE
└── README.md
```

## Features

- Automated document processing and classification
- PDF processing with OCR capabilities
- Intelligent workflow management
- Integration with OSCAR EMR system
- Automated login and session management
- Configurable settings and workflows
- Provider list management
- Extensive error handling and logging

## How It Works

1. **Initialization**: The `OscarAutomation` class in `main.py` initializes the system, loading configurations and setting up logging.
2. **Login**: The `Login` class in `models/login.py` handles automated login to the OSCAR EMR system using Selenium WebDriver.
3. **Session Management**: The `SessionManager` class in `models/session_manager.py` maintains the session for interacting with the OSCAR EMR system.
4. **Document Processing**: The `DocumentProcessor` class in `processors/document_processor.py` handles incoming documents.
5. **PDF Processing**: The `PdfProcessor` class in `processors/pdf_processor.py` specifically handles PDF documents.
6. **Workflow Management**: The `WorkflowProcessor` class in `processors/workflow_processor.py` manages the execution of workflows.

## Configuration and Workflow Management

### Configuration (config/config.yaml)

The `config/config.yaml` file contains the following key configurations:

- `base_url`: OSCAR EMR base URL
- `user_login`: Credentials for OSCAR EMR
- `last_processed_pdf`: Timestamp of the last processed PDF
- `enable_ocr_gpu`: Boolean to enable/disable GPU for OCR
- `workflow_file_path`: Path to the main workflow file
- `chrome_options`: Options for Chrome WebDriver
- `ai_config`: Configuration for the AI model API
- `logging`: Logging configuration
- `categories`: List of document categories

### Workflow Configurations (src/workflows/*.csv)

Workflows are defined in CSV files in the `src/workflows/` directory. Each CSV file represents a specific workflow for different document types. The main workflow files are:

1. `0.csv`: Initial document classification workflow
2. `1.csv`: Consultation letter processing workflow
3. `2.csv`: Insurance and legal document processing workflow
4. `3.csv`: Medical records processing workflow
5. `4.csv`: Health records processing workflow
5. `5.csv`: Diagnostic imaging report processing workflow
6. `6.csv`: Pathology report processing workflow
7. `7.csv`: Communication and notification processing workflow
8. `8.csv`: Lab result processing workflow
9. `9.csv`: Consent form processing workflow
10. `10.csv`: Diagnostic test result processing workflow
11. `11.csv`: Pharmacy-related document processing workflow
12. `12.csv`: Referral and requisition processing workflow
13. `13.csv`: Referral processing workflow
14. `14.csv`: Request for medical records processing workflow
15. `15.csv`: Advertisement and announcement processing workflow

Each CSV file contains rows with the following structure:
- Task number
- Function name to execute
- Function parameters
- Next task number if successful
- Next task number if unsuccessful

### Current Behavior and Workflow

The AI-MOA system follows these general steps:

1. **Document Intake**: 
   - The system processes new documents as they are added to the system.

2. **Initial Classification** (`0.csv`):
   - OCR is performed if necessary using `extract_text_doctr()` or `extract_text_from_pdf_file()`.
   - The document is classified using AI analysis with `build_prompt()`.
   - Based on the classification, the appropriate sub-workflow is selected.

3. **Specific Document Processing**:
   - Each document type (1.csv to 15.csv) has its own workflow for extracting relevant information.
   - Common steps across workflows include:
     - Extracting document description with `get_document_description()`
     - Identifying the requesting provider with `getProviderList()`
     - Searching for patient information with various methods like `get_patient_name()`, `patientSearch()`
     - Filtering and setting patient and doctor information with `filter_results()`, `set_patient()`, `set_doctor()`

4. **EMR Update**:
   - After processing, the document information is updated in the OSCAR EMR using `oscar_update()`.

5. **Error Handling and Logging**:
   - Extensive error handling and logging are implemented throughout the workflow.

## AI Integration

- The system uses a local AI model accessed via API (configured in `ai_config` in config.yaml).
- AI prompts are constructed based on the extracted document text and specific tasks.
- The `build_prompt()` and `build_sub_prompt()` methods in the `Workflow` class handle AI interactions.

## OSCAR EMR Integration

- The system interacts with OSCAR EMR for patient and provider searches, and document updates.
- The `OscarProviderList` class in `utils/OscarProviderList.py` manages provider information.

## Setup and Usage

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `config/config.yaml`
4. Ensure Chrome WebDriver is installed
5. Run the system: `python src/main.py`

## Error Handling and Logging

- Logging is configured in `utils/logging_setup.py`
- Logs are written to both console and file
- Extensive error handling is implemented throughout the application

## Testing

It's recommended to add a `tests/` directory and implement unit tests for the various components of the system.

## Contributing

Contributions to improve AI-MOA are welcome. Please follow the standard fork, branch, and pull request workflow.

## License

This project is licensed under the GNU Affero General Public License v3.0. See the LICENSE file for details.

## Disclaimer

This software is provided "AS IS" without warranty of any kind. Ensure compliance with all relevant medical data privacy regulations when using this software.

## Contributing

Contributions to improve AI-MOA are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

Please ensure that your code adheres to the existing style conventions and includes appropriate tests and documentation.

## License

This project is licensed under the GNU Affero General Public License v3.0. See the LICENSE file for details.

## Disclaimer

This software is provided "AS IS" without warranty of any kind. It is intended for use in medical office settings but should be thoroughly tested and validated before use in any critical systems. Ensure compliance with all relevant medical data privacy regulations (e.g., HIPAA) when using this software.

## Support

For questions, bug reports, or feature requests, please open an issue on the GitHub repository.
