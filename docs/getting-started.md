# Getting Started with AI-MOA

## Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- Chrome WebDriver (for Selenium-based operations)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-org/ai-moa.git
   cd ai-moa
   ```

2. Create a virtual environment:
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
   cd src/
   huey_consumer main.huey
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

## Next Steps

- Read the [Architecture Overview](architecture.md) to understand the system structure
- Learn about [Configuration Options](configuration.md)
- Explore the [API Reference](api-reference.md) for detailed information on classes and methods
