# AI-MOA Configuration Guide

AI-MOA uses two main configuration files:

1. `src/config.yaml`: General system settings
2. `src/workflow-config.yaml`: Workflow and document processing settings

## config.yaml

### Huey Configuration

```yaml
huey:
  name: workflow_queue
  results: True
  store_none: False
  always_eager: True
  file_level: INFO
  console_level: INFO
```

- `name`: Name of the Huey task queue
- `results`: Whether to store task results
- `store_none`: Whether to store None results
- `always_eager`: Run tasks immediately for testing
- `file_level`: Log level for file output.
- `console_level`: Log level for console_level output.

Note: Huey is configured to use in-memory storage only. No SQLite or Redis backend is used.

### Logging Configuration

```yaml
logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  filename: 'workflow.log'
  file_level: DEBUG
  console_level: INFO
```

- `level`: Overall logging level
- `format`: Log message format
- `filename`: Log file name
- `file_level`: Logging level for file output
- `console_level`: Logging level for console output

### EMR Configuration

```yaml
emr:
  base_url: 'http://localhost:8080/oscar'
  username: 'admin'
  password: 'admin'
  pin: '1234'
```

- `base_url`: Base URL of the O19 EMR system
- `username`: EMR login username
- `password`: EMR login password
- `pin`: Pin for EMR login

### OCR Configuration

```yaml
ocr:
  device: cuda:0
  enable_gpu: False
```

- `device`: Device used for OCR processing
- `enable_gpu`: Whether to use GPU for OCR

### File Processing

```yaml
file_processing:
  input_directory: '/app/input'
  output_directory: '/app/output'
  allowed_extensions: ['.pdf', '.jpg', '.png', '.tiff']
```

- `input_directory`: Directory for input files
- `output_directory`: Directory for processed output
- `allowed_extensions`: List of allowed file extensions

## workflow-config.yaml

This file defines:

1. Workflow steps
2. Document categories
3. AI prompts for each processing step

Example structure:

```yaml
workflow:
  steps:
    - name: has_ocr
      true_next: extract_text_from_pdf_file
      false_next: extract_text_doctr

document_categories:
  - name: Lab
    description: "Laboratory test results..."
    tasks:
      - name: get_document_description
        prompt: "Act as if you are a medical office assistant..."

ai_prompts:
  build_prompt: "For the following question, if confidence level is more than 85%..."
  get_patient_name: "Answer only to the following question in two words..."
```

For detailed explanations of each configuration option, refer to the comments in the example configuration files.
