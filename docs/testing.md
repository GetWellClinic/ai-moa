# AI-MOA Testing Guide

This guide outlines the testing procedures for the AI-MOA project, including unit tests, integration tests, and end-to-end tests.

## Unit Tests

Unit tests are located in the `tests/unit/` directory. They test individual components and functions in isolation.

To run unit tests:

```
python -m unittest discover tests/unit
```

### Writing Unit Tests

1. Create a new test file in `tests/unit/` for each module you're testing
2. Use Python's `unittest` framework
3. Follow the naming convention `test_*.py` for test files
4. Use descriptive test method names that explain the scenario being tested

Example:

```python
import unittest
from src.auth.login_manager import LoginManager

class TestLoginManager(unittest.TestCase):
    def test_login_with_valid_credentials(self):
        # Test implementation

    def test_login_with_invalid_credentials(self):
        # Test implementation
```

## Integration Tests

Integration tests are located in `tests/integration/`. They test the interaction between different components of the system.

To run integration tests:

```
python -m unittest discover tests/integration
```

### Writing Integration Tests

1. Create test files in `tests/integration/`
2. Focus on testing the interaction between multiple components
3. Use mocks or stubs for external services when necessary

Example:

```python
import unittest
from unittest.mock import patch
from src.processors.pdf.pdf_processor import PdfProcessor

class TestPdfProcessorIntegration(unittest.TestCase):
    @patch('src.auth.session_manager.SessionManager')
    def test_pdf_processing_workflow(self, mock_session_manager):
        # Test implementation
```

## End-to-End Tests

End-to-end tests are located in `tests/e2e/`. They test the entire system from start to finish.

To run end-to-end tests:

```
python -m unittest discover tests/e2e
```

### Writing End-to-End Tests

1. Create test files in `tests/e2e/`
2. Simulate real-world usage scenarios
3. Use actual configuration files and test data

Example:

```python
import unittest
from src.main import AIMOAAutomation

class TestFullWorkflow(unittest.TestCase):
    def test_complete_document_processing(self):
        automation = AIMOAAutomation()
        # Test the entire workflow
```

## Test Data

Test data is stored in `tests/data/`. This includes sample PDFs, documents, and configuration files for testing.

## Continuous Integration

The project uses GitHub Actions for continuous integration. The CI pipeline is defined in `.github/workflows/ci.yml`.

The CI pipeline runs:
1. Linting with flake8
2. Unit tests
3. Integration tests
4. End-to-end tests


## Coverage Reports

To generate test coverage reports:

1. Install coverage: `pip install coverage`
2. Run tests with coverage: `coverage run -m unittest discover testing/`
3. Generate report: `coverage report -m`
4. For HTML report: `coverage html`

Aim for a test coverage of at least 80% for critical components.

Remember to update tests whenever you add new features or modify existing functionality.
