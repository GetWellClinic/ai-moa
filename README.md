# AI-MOA (AI-powered Medical Office Assistant)

AI-MOA is an advanced, AI-powered Medical Office Assistant designed to automate various tasks in a medical office setting. It focuses on document processing, workflow management, and seamless integration with the O19 Electronic Medical Record (EMR) system.

## Features

- Automated document processing and classification using AI
- Advanced PDF processing with OCR capabilities
- Intelligent workflow management system
- Seamless integration with O19 EMR system
- Automated login and session management
- Highly configurable settings and workflows
- Comprehensive provider list management
- Robust error handling and detailed logging
- Docker support for easy deployment and scaling
- Task queue management with Huey (in-memory storage)

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

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-org/ai-moa.git
   cd ai-moa
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r src/requirements.txt
   ```

4. Configure the application:
   - Copy `src/config.yaml.example` to `src/config.yaml` and update the settings
   - Copy `src/workflow-config.yaml.example` to `src/workflow-config.yaml` and customize the workflow

5. Run the application:
   ```
   python src/main.py
   ```

## Docker Setup

1. Build the Docker image:
   ```
   docker build -t ai-moa .
   ```

2. Run the container:
   ```
   docker-compose up
   ```

## Testing

To run the tests:

1. Unit tests: `python -m unittest discover tests/unit`
2. Integration tests: `python -m unittest discover tests/integration`
3. Full workflow test: `python testing/full_workflow_test.py`
4. Prompt testing: `python testing/prompt_testing_script.py`

## Contributing

Contributions to AI-MOA are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run the tests to ensure everything is working
5. Commit your changes (`git commit -am 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Create a new Pull Request

Please read [CONTRIBUTING.md](docs/contributing.md) for more details on our code of conduct and development process.

## License

This project is licensed under the GNU Affero General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Support

For questions, bug reports, or feature requests, please open an issue on the GitHub repository.
