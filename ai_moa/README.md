# AI-MOA (AI-powered Medical Office Assistant)

This project is an AI-powered Medical Office Assistant designed to automate various tasks in a medical office setting, particularly focusing on document processing and workflow management.

## Project Structure

```
ai_moa/
├── config/
│   └── config.yaml
├── src/
│   ├── models/
│   │   └── login.py
│   ├── processors/
│   │   ├── document_processor.py
│   │   ├── pdf_processor.py
│   │   └── workflow_processor.py
│   ├── utils/
│   │   ├── config_loader.py
│   │   ├── logging_setup.py
│   │   └── ocr_utils.py
│   ├── main.py
│   └── oscar_automation.py
└── README.md
```

## Features

- Document processing
- PDF processing
- Workflow management
- OCR capabilities
- Automated login

## Setup

1. Clone the repository
2. Install the required dependencies (list them or refer to a requirements.txt file)
3. Configure the `config.yaml` file with your settings
4. Run the main.py script

## Usage

To run the AI-MOA:

```
python src/main.py
```

This will start the automation process, including document processing, PDF processing, and workflow management.

## Configuration

Edit the `config/config.yaml` file to set up your:

- Base URL
- Login credentials
- OCR settings
- File paths

## Contributing

(Add contribution guidelines if applicable)

## License

(Add license information)
