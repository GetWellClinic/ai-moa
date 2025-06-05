#!/bin/bash
# Startup script for AI-MOA

# Version 2025.05.10

# CONFIGURATION:
# Automatic configuration of paths:
CURRENT=$(pwd)
cd ..
AIMOA=$(pwd)
AIPYTHONENV=$(pwd)/.env
# Override by specifying the full path for AI-MOA base directory and Python virtual environment that contains the installed python pre-requisite packages:
# AIMOA=/opt/ai-moa
# AIPYTHONENV=/opt/virtualenv/aimoa

# Confirm base directory of AI-MOA:
/bin/echo "Currently specifying the following as the base directory for AI-MOA..."
/bin/echo $AIMOA
/bin/echo ""
/bin/echo "This 'run-aimoa-incomingfax.sh' is for starting AI-MOA by command line. You do not need to run this if you have installed AI-MOA as a system service."
/bin/echo "	( Hint: To install AI-MOA as a system service, execute 'sudo ./install-aimoa.sh' )"
/bin/sleep 3s

# Activate Python virtual environment with installed pre-requisite packages
source $AIPYTHONENV/bin/activate

# Export environment variables specifying location of config files
export CONFIG_FILE=$AIMOA/config/config-incomingfax.yaml
export WORKFLOW_CONFIG_FILE=$AIMOA/config/workflow-config-incomingfax.yaml

# Option to disable warnings when using a self-signed SSL certificate for servers, quiet the logging
export PYTHONWARNINGS="ignore:Unverified HTTPS request"

# Display environment variables on console
/bin/echo "Specifying the following environmental variables for AI-MOA..."
/bin/echo $CONFIG_FILE
/bin/echo $WORKFLOW_CONFIG_FILE
/bin/echo $PYTHONWARNINGS

# Initialize permissions (otherwise AI-MOA can't read-wrote config files, or save provider list)
#/bin/chown aimoa:aimoa $AIMOA/src/* 2>/dev/null
/bin/chown aimoa:aimoa $AIMOA/config/* 2>/dev/null
/bin/chmod g+rw $AIMOA/config -R 2>/dev/null
#/bin/chmod g+rw $AIMOA/src/* 2>/dev/null

# Command to start AI-MOA
/bin/echo "Starting AI-MOA..."
# main version
cd $AIMOA/src
python3 main.py --config $AIMOA/config/config-incomingfax.yaml --workflow-config $AIMOA/config/workflow-config-incomingfax.yaml --reset-lock --cron-interval */1 --run-immediately
# (huey version)
# huey_consumer main.huey

# Returning to previous path location
cd $CURRENT
