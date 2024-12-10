#!/bin/bash
# Startup script for AI-MOA

# Version 2024.12.09

# CONFIGURATION:
# Automatic configuration of paths:
CURRENT=$(pwd)
cd ..
AIMOA=$(pwd)
AIPYTHONENV=$(pwd)/.venv
# Override by specifying the full path for AI-MOA base directory and Python virtual environment that contains the installed python pre-requisite packages:
# AIMOA=/opt/ai-moa
# AIPYTHONENV=/opt/virtualenv/aimoa

# Confirm base directory of AI-MOA:
/bin/echo "Currently specifying the following as the base directory for AI-MOA..."
/bin/echo $AIMOA
/bin/echo ""
/bin/echo "This 'run-aimoa.sh' is for starting AI-MOA by command line. You do not need to run this if you have installed AI-MOA as a system service."
/bin/echo "	( Hint: To install AI-MOA as a system service, execute 'sudo ./install-aimoa.sh' )"
/bin/sleep 3s

# Activate Python virtual environment with installed pre-requisite packages
source $AIPYTHONENV/bin/activate

# Export environment variables specifying location of config files
export CONFIG_FILE=$AIMOA/config/config.yaml
export WORKFLOW_CONFIG_FILE=$AIMOA/config/workflow-config.yaml

# Option to disable warnings when using a self-signed SSL certificate for servers, quiet the logging
export PYTHONWARNINGS="ignore:Unverified HTTPS request"

# Display environment variables on console
/bin/echo "Specifying the following environmental variables for AI-MOA..."
/bin/echo $CONFIG_FILE
/bin/echo $WORKFLOW_CONFIG_FILE
/bin/echo $PYTHONWARNINGS

# Command to start AI-MOA (dev-gwc/huey version)
/bin/echo "Starting AI-MOA..."
cd $AIMOA/src
huey_consumer main.huey

# Returning to previous path location
cd $CURRENT
