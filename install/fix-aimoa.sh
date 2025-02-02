#!/bin/bash
# This script fixes some common errors with AI-MOA Note:
# To correctly use automatic detection of AI-MOA path, this script must be installed and run in subdirectory 'gwc-aimee'
# This install script should be run as 'sudo ./fix-aimoa.sh'
# Version 2025.02.02

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

# Add default first administrator username to "aimoa" group
USERNAME=$(awk -F':' -v uid=1000 '$3 == uid { print $1 }' /etc/passwd)
/usr/sbin/usermod -a -G aimoa "$USERNAME"

# Modify user:group permissions:
/bin/chown aimoa:aimoa $AIMOA/* -R
/bin/chown aimoa:aimoa $AIMOA/.env/* -R -P
# Fix permissions so AI MOA can read-write
/bin/chmod ug+rwx $AIMOA/config $AIMOA/logs $AIMOA/.env $AIMOA/src/config
/bin/chmod ug+rw $AIMOA/config/* $AIMOA/logs/* $AIMOA/.env/* $AIMOA/src/config/*.yaml
/bin/chmod ug+rw $AIMOA/llm-container/models
/bin/chmod ug+rw $AIMOA/src/*.lock $AIMOA/config/*.lock
# Protect config.yaml from Other users
/bin/chmod o-rwx $AIMOA/config

/bin/echo "Confirming current user belonging to the following groups (check for 'aimoa')..."
/usr/bin/groups $USER
/usr/bin/groups $USERNAME
/bin/echo ""
/bin/sleep 5s

# Protect installation files
/bin/chmod guo+x $AIMOA/install/*
/bin/chmod o-x $AIMOA/install/install*
/bin/chmod o-x $AIMOA/install/uninstall*
# Protect config directory
/bin/chmod o-rw ../config/config.yaml*

# Release file lock on workflow-config.yaml
# release_lock

# Reminder to add username to group aimoa
/bin/echo ""
/bin/echo "Remember to also add your username to "aimoa" group so your username can run AI-MOA...!"
/bin/echo "		(sudo usermod -a -G aimoa username)"
/bin/echo ""