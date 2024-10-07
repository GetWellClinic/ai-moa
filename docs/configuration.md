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
  schedule:
    minute: '*/5'
  filename: '/app/oscar_tasks.db'
```

- `name`: Name of the Huey task queue
- `results`: Whether to store task results
- `store_none`: Whether to store None results
- `always_eager`: Run tasks immediately for testing
- `schedule`: Cron-style schedule for periodic tasks
- `filename`: SQLite database file for task storage

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
```

- `base_url`: Base URL of the O19 EMR system
- `username`: EMR login username
- `password`: EMR login password

### OCR Configuration

```yaml
ocr:
  enable_gpu: False
  tesseract_path: '/usr/bin/tesseract'
```

- `enable_gpu`: Whether to use GPU for OCR
- `tesseract_path`: Path to Tesseract OCR executable

### File Processing

```yaml
file_processing:
  input_directory: '/app/input'
  output_directory: '/app/output'
  allowed_extensions: ['.pdf', '.jpg', '.png', '.tiff']
  temp_pdf_name: "downloaded_pdf.pdf"
```

- `input_directory`: Directory for input files
- `output_directory`: Directory for processed output
- `allowed_extensions`: List of allowed file extensions
- `temp_pdf_name`: Temporary name for downloaded PDFs

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
