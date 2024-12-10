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
│   ├── ai_moa_utils/
│   │   ├── __init__.py
│   │   └── logging_setup.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── driver_manager.py
│   │   ├── login_manager.py
│   │   └── session_manager.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   └── provider_list_manager.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── document_tagger/
│   │   │   ├── __init__.py
│   │   │   └── document_category.py
│   │   ├── o19/
│   │   │   ├── __init__.py
│   │   │   ├── o19_inbox.py
│   │   │   └── o19_updater.py
│   │   ├── patient_tagger/
│   │   │   ├── __init__.py
│   │   │   └── patient.py
│   │   ├── provider_tagger/
│   │   │   ├── __init__.py
│   │   │   └── provider.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── llm.py
│   │   │   ├── local_files.py
│   │   │   └── ocr.py
│   │   └── workflow/
│   │       ├── __init__.py
│   │       └── emr_workflow.py
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
   git clone https://github.com/GetWellClinic/ai-moa.git
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
   - Configure the src/config.yaml and update the settings
   - Configure the src/workflow-config.yaml and customize the workflow

5. Run the application:
   ```
   cd src/
   python main.py
   ```
   
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

## For Developers

See the [DEVELOPERS.md](docs/developers.md) file for details.

## License

This project is licensed under the GNU Affero General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Support

For questions, bug reports, or feature requests, please open an issue on the GitHub repository.
