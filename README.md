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

4. **Document Processing**:
   - The `DocumentProcessor` class in `processors/document_processor.py` handles incoming documents.
   - It uses OCR (Optical Character Recognition) to extract text from documents if needed.
   - The extracted text is then processed to classify the document and extract relevant information.

5. **PDF Processing**:
   - The `PdfProcessor` class in `processors/pdf_processor.py` specifically handles PDF documents.
   - It can download PDFs from the OSCAR system and process them using the `Workflow` class.

6. **Workflow Management**:
   - The `WorkflowProcessor` class in `processors/workflow_processor.py` manages the execution of workflows.
   - Workflows are defined in CSV files in the `workflows/` directory.

## Workflow Management

The AI-MOA system uses a flexible and powerful workflow management system to process documents and interact with the OSCAR EMR. Here's a detailed explanation of how it works:

### Workflow Structure

1. **CSV-based Task Definition**: Workflows are defined in CSV files (e.g., `workflow.csv`, `0.csv`, `1.csv`, etc.) in the `workflows/` directory. Each CSV file represents a specific workflow or sub-workflow.

2. **Task Format**: Each row in a CSV file represents a task and contains the following columns:
   - Task number
   - Function name to execute
   - Function parameters (variable number)
   - Next task number if successful
   - Next task number if unsuccessful

3. **Workflow Class**: The `Workflow` class in `utils/workflow.py` is the core component that executes these tasks.

### Workflow Execution Process

1. **Initialization**: The `Workflow` class is initialized with document information, session details, and configuration settings.

2. **Task Execution**: The `execute_tasks_from_csv` method is called, which:
   - Reads tasks from the appropriate CSV file
   - Starts execution from the first task (row 0)

3. **Task Processing**: For each task, the system:
   - Calls the specified function with given parameters
   - Evaluates the result
   - Determines the next task to execute based on success or failure

4. **Dynamic Flow**: The workflow can branch and jump between tasks based on results, allowing for complex decision-making processes.

5. **Function Mapping**: The `Workflow` class dynamically maps function names from the CSV to actual method calls, allowing for flexible task definitions.

### Key Components

- **Document Processing**: Functions for OCR, text extraction, and document classification.
- **EMR Interaction**: Methods to search for patients, providers, and update OSCAR EMR.
- **AI Integration**: Calls to AI models for document analysis and decision-making.
- **Data Management**: Functions to set and retrieve patient and provider information.

### Customization and Extension

- New workflows can be easily defined by creating new CSV files in the `workflows/` directory.
- Additional functions can be added to the `Workflow` class to extend capabilities.
- The system supports different workflows for various document types (lab reports, consultations, etc.).

## AI Integration

- The system uses a local AI model (accessed via API) to assist in document classification and information extraction.
- AI prompts are constructed based on the extracted document text and specific tasks.
- The AI integration is configurable through the `config.yaml` file.

## OSCAR EMR Integration

- The system can search for patients and providers in OSCAR.
- It can update OSCAR with processed document information, including attaching documents to patient records.
- The `OscarProviderList` class in `utils/OscarProviderList.py` manages the retrieval and caching of provider information from OSCAR.

## Setup

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure the `config/config.yaml` file with your OSCAR EMR settings and other configurations
4. Ensure you have Chrome WebDriver installed for Selenium
5. Set up the local AI model API (instructions should be provided separately)

## Usage

To run the AI-MOA:

```
python src/main.py
```

This will start the automation process, including document processing, PDF processing, and workflow management.

## Configuration

Edit the `config/config.yaml` file to set up your:

- OSCAR EMR base URL
- Login credentials
- OCR settings (GPU enabled/disabled)
- File paths for documents and workflows
- Logging settings
- AI model configuration
- Chrome WebDriver options

The `ConfigManager` class in `utils/config_manager.py` provides a centralized way to access and manage these configuration settings throughout the application.

## Logging

The application uses Python's built-in logging module, configured in `utils/logging_setup.py`. Logs are written to both console and file, with configurable log levels and formats.

## Error Handling

Extensive error handling is implemented throughout the application to ensure robustness and provide detailed error information for troubleshooting.

## Testing

While not explicitly shown in the provided structure, it's recommended to add a `tests/` directory and implement unit tests for the various components of the system.

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
