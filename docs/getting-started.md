# Getting Started with AI-MOA

## Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- Chrome WebDriver (for Selenium-based operations)
- [llm-container.md](docs/llm-container.md)

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

   Once your virtual environment is active, navigate to the src/ directory (if not already in it) and run the `install.sh` script to install all required dependencies.

   `cd src/`

   Make the install.sh script executable

   `chmod +x install.sh`

   Run the installation script

   `./install.sh`

   The `install.sh` script will handle the installation of Python dependencies and any other setup required for the project.


4. Configure the application:

   - Copy `src/config.yaml.example` to `src/config.yaml` and update the settings
   - Copy `src/workflow-config.yaml.example` to `src/workflow-config.yaml` and customize the workflow

   Before running the command (Step 5), make sure to add the paths to config.yaml and workflow-config.yaml to the environment variables `CONFIG_FILE` and `WORKFLOW_CONFIG_FILE`.

   Example of Setting Environment Variables:
   If you're running the command in a terminal or shell, you can set the environment variables like this:

   On Linux/macOS (Bash shell):

   export CONFIG_FILE=/path/to/config.yaml
   export WORKFLOW_CONFIG_FILE=/path/to/workflow-config.yaml
   echo $CONFIG_FILE
   echo $WORKFLOW_CONFIG

   On Windows (Command Prompt):

   set CONFIG_FILE=C:\path\to\config.yaml
   set WORKFLOW_CONFIG_FILE=C:\path\to\workflow-config.yaml

   Please read [basic-installation-details.md](docs/basic-installation-details.md) for more details


5. Run the application:
   ```
   cd src/
   huey_consumer main.huey
   ```


## Next Steps

- Read the [Architecture Overview](architecture.md) to understand the system structure
- Learn about [Configuration Options](configuration.md)
- Explore the [API Reference](api-reference.md) for detailed information on classes and methods
