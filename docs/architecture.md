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

### 4. PDF Processing

- Location: `src/processors/pdf/`
- Key Classes:
  - `PdfProcessor`: Manages PDF document processing
  - `PdfFetcher`: Retrieves PDF content from O19 EMR
  - OCR functionality in `ocr.py`

### 5. Workflow Management

- Location: `src/processors/workflow/`
- Key Classes:
  - `WorkflowProcessor`: Orchestrates workflow execution
  - `WorkflowStepExecutor`: Executes individual workflow steps
  - `WorkflowTaskManager`: Manages Huey tasks for workflows
- Uses Huey for task management with in-memory storage

### 6. AI Integration

- Integrated throughout the application
- Uses local AI model via API (configured in `config.yaml`)

### 7. O19 EMR Integration

- Integrated throughout the application
- Interacts with O19 EMR for patient and provider data, document updates

## Data Flow

1. Documents are fetched from O19 EMR
2. Documents are processed (OCR for PDFs)
3. AI model classifies and extracts information
4. Workflow is executed based on document type and content
5. Results are updated in O19 EMR

## Extensibility

The modular architecture allows for easy extension of functionality:
- Add new document processors in `src/processors/`
- Extend workflow steps in `src/processors/workflow/`
- Implement new AI integrations by modifying the `Workflow` class

For more detailed information on each component, refer to the [API Reference](api-reference.md).
