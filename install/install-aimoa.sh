#!/bin/bash
# This custom script installs Get Well Clinic's version of AI-MOA (Aimee AI)
# Note: To correctly use automatic detection of AI-MOA path, this script must be installed and run in subdirectory 'install'
# This install script should be run as 'sudo ./install-aimoa.sh'
# Version 2025.02.21

# Hardware Requirements:
#	NVIDIA RTX video card installed with at least 12 GB VRAM

# Software Requirements:
#	NVIDIA graphics drivers installed
#	Docker installed
#	Docker Compose installed
#	NVIDIA Container Toolkit installed
#	AI-MOA installed in preferably in /opt/ai-moa directory
# 	Python 3.x installed
# 	Python package installed:
#		pip
#		virtualenv
#

# CONFIGURATION:
# 
# Autodetect first administrator username:
USERNAME=$(awk -F':' -v uid=1000 '$3 == uid { print $1 }' /etc/passwd)
# Override username to be added to "aimoa" group permissions, to allow username to run AI-MOA:
# USERNAME=

# Automatic detection of base directory
cd ..
AIMOA=$(pwd)

/bin/echo "AI-MOA (Aimee AI) will be installed and setup with the following specified base directory for AI-MOA..."
/bin/echo ""
/bin/echo "Base directory: "$(pwd)
/bin/echo ""
/bin/echo "...if the above directory is not the correct base directory for AI-MOA, please Ctrl-C to cancel installation now...!"
/bin/sleep 10s
/bin/echo ""
# Create the logs directory if it doesn't exist
/bin/echo "Creating log directory..."
/bin/mkdir -p '$AIMOA/logs'

# Create the static directory if it doesn't exist
/bin/echo "Creating src/static directory..."
/bin/mkdir -p '$AIMOA/src/static'

# Create the config directory if it doesn't exit. For local configuration files.
/bin/echo "Creating config directory"
/bin/mkdir -p '$AIMOA/config'

# Create the app directories if it doesn't exit. For local folder document processing.
/bin/echo "Creating app directories"
/bin/mkdir -p '$AIMOA/app'
/bin/mkdir -p '$AIMOA/app/input'
/bin/mkdir -p '$AIMOA/app/output'

# Initialize permissions
/bin/chmod g+rw '$AIMOA/config' -R
/bin/chmod g+rw '$AIMOA/app/' -R
/bin/chmod g+rw '$AIMOA/src/*'

# Create the llm-container/models directory if it doesn't exist
/bin/echo "Creating llm-container/models directory..."
/bin/mkdir -p '$AIMOA/llm-container/models'

# Backup config files
/bin/echo "Backing up old config files..."
/bin/cp $AIMOA/src/config.yaml $AIMOA/src/config.yaml.$(date +'%Y-%m-%d')
/bin/cp $AIMOA/config/config.yaml $AIMOA/config/config.yaml.$(date +'%Y-%m-%d')
/bin/cp $AIMOA/config/config-incomingfax.yaml $AIMOA/config/config-incomingfax.yaml.$(date +'%Y-%m-%d')
/bin/cp $AIMOA/src/workflow-config.yaml $AIMOA/src/workflow-config.yaml.$(date +'%Y-%m-%d')
/bin/cp $AIMOA/config/workflow-config.yaml $AIMOA/config/workflow-config.yaml.$(date +'%Y-%m-%d')
/bin/cp $AIMOA/config/workflow-config-incomingfax.yaml $AIMOA/config/workflow-config-incomingfax.yaml.$(date +'%Y-%m-%d')
/bin/cp $AIMOA/config/provider_list.yaml $AIMOA/config/provider_list.yaml.$(date +'%Y-%m-%d')
/bin/cp $AIMOA/src/config/provider_list.yaml $AIMOA/src/config/provider_list.yaml.$(date +'%Y-%m-%d')
# Create config files in config directory
/bin/echo "Creating config files from templates..."
/bin/cp $AIMOA/src/config.yaml.example $AIMOA/config/config.yaml
/bin/cp $AIMOA/src/config-incomingfax.yaml.example $AIMOA/config/config-incomingfax.yaml
/bin/cp $AIMOA/src/workflow-config.yaml.example $AIMOA/config/workflow-config.yaml
/bin/cp $AIMOA/src/workflow-config.yaml.example $AIMOA/config/workflow-config-incomingfax.yaml
/bin/cp $AIMOA/src/template_providerlist.txt $AIMOA/config/
/bin/echo "...remember to edit the config files in ../config/* to customize to your installation."
# Initialize installation to re-fresh provider list
/bin/echo "Removing provider_list for clean start..."
/bin/sleep 5s
/bin/rm $AIMOA/config/provider_list.yaml
/bin/rm $AIMOA/src/config/provider_list.yaml
# Missing provider list will cause AI-MOA to regenerate the list

# Confirm your local timezone is set:
/bin/timedatectl
/bin/echo ""
/bin/echo "...please confirm that above details of your system has your correct desired timezone..."
/bin/echo "...if your timezone is not set properly, your document files may be marked with the wrong dates...!"
/bin/echo "	(Hint: use 'timedatectl set-timezone' to change your timezone)"
/bin/sleep 5s

# Create Python virtual environment for AI-MOA libraries and dependency packages:
/bin/echo "Creating python virtual environment for AI-MOA dependencies..."
/bin/sleep 5s
virtualenv $AIMOA/.env
# Install python dependencies for AI-MOA from requirements.txt
/bin/echo "Installing Python libraries and dependencies required for running AI-MOA in python virual environment..."
/bin/sleep 5s
# Activate virtual environment and install in python packages in virtual environment
source $AIMOA/.env/bin/activate
pip install -r $AIMOA/src/requirements.txt

# Create Linux user and group for 'aimoa':
/usr/sbin/useradd -m aimoa	# Requires home directory for google-chrome files
# Add current user to 'aimoa' group
/usr/sbin/usermod -a -G aimoa $USER
/usr/sbin/usermod -a -G aimoa $USERNAME

# Initialize file permissions for AI-MOA:
/bin/echo "Fixing file permissions for AI-MOA to 'rw-rw-r-- aimoa aimoa' ..."
/bin/sleep 5s
# Modify user:group permissions
/bin/chown aimoa:aimoa $AIMOA/* -R
# Fix permissions so AI MOA can read-write
/bin/chmod ug+rwx $AIMOA/config $AIMOA/logs $AIMOA/app $AIMOA/app/input $AIMOA/app/output
/bin/chmod ug+rw $AIMOA/config/* $AIMOA/logs/* $AIMOA/app/input/* $AIMOA/app/output/*
/bin/chmod ug+rw $AIMOA/llm-container/models
# Protect config.yaml from Other users
/bin/chmod o-rwx $AIMOA/config
# Confirm user belongs to group "aimoa"
/bin/echo "Confirming current user belonging to the following groups (check for 'aimoa')..."
/usr/bin/groups $USER
/usr/bin/groups $USERNAME
/bin/echo ""
/bin/sleep 5s

# Protect installation files
/bin/echo "Enabling scripts, and protecting installation files..."
/bin/chmod guo+x $AIMOA/install/*
/bin/chmod o-x $AIMOA/install/install*
/bin/chmod o-x $AIMOA/install/uninstall*
# Protect directories from Other Users
/bin/echo "Protecting ../config directory..."
/bin/chmod o-rwx $AIMOA/config
/bin/echo "Protecting ../app directory..."
/bin/chmod o-rwx $AIMOA/app -R

# Install google-chrome
/bin/echo "Installing Google Chrome for AI-MOA..."
/bin/echo "...adding Chrome repository to system sources..."
# Add Chrome repository key to keychain
/bin/wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
# Add Chrome repo to system sources
/bin/echo "deb http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee -a /etc/apt/sources.list.d/google.list
apt-get update
# Install google-chrome-stable
apt-get -y install google-chrome-stable

