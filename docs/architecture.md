# AI-MOA Architecture

## High-Level Overview

AI-MOA is structured as a modular Python application with the following main components:

1. Authentication and Session Management
2. Configuration Management
3. Document Processing
4. PDF Processing
5. Workflow Management
6. AI Integration
7. O19 EMR Integration
8. Logging and Error Handling

## Component Breakdown

### 1. Authentication and Session Management

- Location: `src/auth/`
- Key Classes:
  - `LoginManager`: Handles login to O19 EMR
  - `SessionManager`: Maintains active sessions
  - `DriverManager`: Manages Selenium WebDriver instances

### 2. Configuration Management

- Location: `src/config/`
- Key Classes:
  - `ConfigManager`: Loads and manages application configuration
  - `ProviderListManager`: Manages provider information

### 3. Document Processing

- Location: `src/processors/document/`
- Key Classes:
  - `DocumentProcessor`: Handles general document processing
  - `LocalFileProcessor`: Processes documents from local filesystem
  - `O19Processor`: Processes documents from O19 EMR

### 4. PDF Processing

- Location: `src/processors/pdf/`
- Key Classes:
  - `PdfProcessor`: Manages PDF document processing
  - `PdfFetcher`: Abstract base class for PDF fetching
  - `O19PdfFetcher`: Retrieves PDF content from O19 EMR
  - `LocalPdfFetcher`: Retrieves PDF content from local filesystem
  - OCR functionality in `ocr.py`

### 5. Workflow Management

- Location: `src/processors/workflow/`
- Key Classes:
  - `WorkflowProcessor`: Orchestrates workflow execution
  - `WorkflowStepExecutor`: Executes individual workflow steps
  - `WorkflowTaskManager`: Manages Huey tasks for workflows
  - `Workflow`: Defines and executes the main workflow logic
- Uses Huey for task management with in-memory storage

### 6. AI Integration

- Integrated throughout the application
- Uses local AI model via API (configured in `config.yaml`)
- AI prompts defined in `workflow-config.yaml`

### 7. O19 EMR Integration

- Integrated throughout the application
- Interacts with O19 EMR for patient and provider data, document updates

### 8. Logging and Error Handling

- Location: `src/logging/`
- Key Module:
  - `logging_setup.py`: Configures logging for the entire application
- Comprehensive error handling and logging throughout all components

## Data Flow

1. Documents are fetched from O19 EMR or local filesystem
2. Documents are processed (OCR for PDFs)
3. AI model classifies and extracts information
4. Workflow is executed based on document type and content
5. Results are updated in O19 EMR or local filesystem

## Shared State Mechanism

AI-MOA implements a shared state mechanism to pass information between workflow tasks. This is achieved through the `ConfigManager` class, which provides methods to set, get, and clear shared state data.

- Location: `src/config/config_manager.py`
- Key Methods:
  - `set_shared_state(key, value)`: Stores a value in the shared state
  - `get_shared_state(key, default=None)`: Retrieves a value from the shared state
  - `clear_shared_state()`: Clears all shared state data

The shared state is used within the `Workflow` class to pass data between different steps of the workflow execution.

## Extensibility

The modular architecture allows for easy extension of functionality:
- Add new document processors in `src/processors/`
- Extend workflow steps in `src/processors/workflow/`
- Implement new AI integrations by modifying the `Workflow` class
- Add support for new EMR systems by creating new processor classes

## Security Considerations

- Secure handling of credentials and sensitive data
- HTTPS communication with EMR and AI services
- Input validation and sanitization throughout the application

## Performance Optimization

- Asynchronous task execution with Huey
- Efficient PDF processing with PyMuPDF
- Caching mechanisms for frequently accessed data

For more detailed information on each component, refer to the [API Reference](api-reference.md).
