# AIMOA Installation Guide (without docker container)

This guide will walk you through the steps to set up and install **AIMOA** on your local machine. Follow these steps carefully to get the project up and running.

## Prerequisites

Before starting, make sure you have the following installed:

- **Python 3.x** (preferably Python 3.10+)
- **pip** (Python's package installer)
- **Git** (for cloning the repository)
- **Google Chrome Browser**

## Steps for Installation

### 1. Clone the Repository

First, clone the repository to your local machine. Open your terminal and run the following command:

`git clone https://github.com/GetWellClinic/ai-moa.git`

Checkout the branch you will be using. For example, git checkout dev-gwc

### 2. Create and Activate the Virtual Environment
Create a Python virtual environment for the project. This step ensures that the dependencies are installed in an isolated environment and do not interfere with your system's Python environment.

Run the following command to create the virtual environment:

`python -m venv aimoa`

Next, activate the virtual environment:

On Linux/macOS:

`source aimoa/bin/activate`

On Windows:

`.\aimoa\Scripts\activate`

When the virtual environment is activated, your terminal prompt should change to show the virtual environment name (e.g., (aimoa)).

### 3. Install Dependencies

Once your virtual environment is active, navigate to the src/ directory (if not already in it) and run the `install.sh` script to install all required dependencies.

`cd src/`

Make the install.sh script executable

`chmod +x install.sh`

Run the installation script

`./install.sh`

The `install.sh` script will handle the installation of Python dependencies and any other setup required for the project.

### 4. Running the Application

After installation, you can run the application by executing:

`huey_consumer main.huey`

Before running the command, make sure to add the paths to config.yaml and workflow-config.yaml to the environment variables `CONFIG_FILE` and `WORKFLOW_CONFIG_FILE`.

Example of Setting Environment Variables:
If you're running the command in a terminal or shell, you can set the environment variables like this:

On Linux/macOS (Bash shell):

export CONFIG_FILE=/path/to/config.yaml
export WORKFLOW_CONFIG_FILE=/path/to/workflow-config.yaml

On Windows (Command Prompt):

set CONFIG_FILE=C:\path\to\config.yaml
set WORKFLOW_CONFIG_FILE=C:\path\to\workflow-config.yaml

### 5. (Optional) Deactivating the Virtual Environment
Once you're done working with the project, you can deactivate the virtual environment by simply running:

`deactivate`

This will return you to the global Python environment.

## Troubleshooting

Missing Dependencies: If you encounter errors about missing packages, ensure you’ve followed all the steps in the installation process, and that you’re working in the correct virtual environment. You can reinstall the dependencies by running `pip install -r requirements.txt`.
Permissions Issues: If you run into permission-related errors, especially when trying to execute the `install.sh script`, try running it with sudo (on Linux/macOS):

`sudo ./install.sh`

Or ensure you have the necessary permissions set on the script using `chmod +x install.sh`.