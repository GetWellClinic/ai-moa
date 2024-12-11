#!/bin/bash
# This script fixes some common errors with AI-MOA Note:
# To correctly use automatic detection of AI-MOA path, this script must be installed and run in subdirectory 'gwc-aimee'
# This install script should be run as 'sudo ./fix-aimoa.sh'
# Version 2024.12.10

# CONFIGURATION:
CURRENT=$(pwd)
# Automatic detection of AI-MOA base directory:
cd ..
AIMOA=$(pwd)
# Override with path to AI-MOA base directory:
# AIMOA=/opt/ai-moa

# Fixing file permissions for AI-MOA:
/bin/echo "Fixing file permissions for AI-MOA to 'rw-rw-r-- aimoa aimoa' ..."
/bin/sleep 5s

# Modify user:group permissions:
/bin/chown aimoa:aimoa $AIMOA/* -R
# Fix permissions so AI MOA can read-write
/bin/chmod ug+rwx $AIMOA/config $AIMOA/logs
/bin/chmod ug+rw $AIMOA/config/* $AIMOA/logs/*
# Protect config.yaml from Other users
/bin/chmod o-rwx $AIMOA/config

/bin/echo "Confirming current user belonging to the following groups (check for 'aimoa')..."
/usr/bin/groups $USER
/bin/echo ""
/bin/sleep 5s

# Protect installation files
/bin/chmod guo+x $AIMOA/gwc-aimee/*
/bin/chmod o-x $AIMOA/gwc-aimee/install*
/bin/chmod o-x $AIMOA/gwc-aimee/uninstall*
# Protect config directory
/bin/chmod o-rw ../config/config.yaml*

# Release file lock on workflow-config.yaml
# release_lock
