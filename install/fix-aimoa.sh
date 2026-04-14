#!/bin/bash
# This script fixes some common errors with AI-MOA Note:
# To correctly use automatic detection of AI-MOA path, this script must be installed and run in subdirectory 'gwc-aimee'
# This install script should be run as 'sudo ./fix-aimoa.sh'
# Version 2025.05.28

# CONFIGURATION:
CURRENT=$(pwd)
USER=${SUDO_USER:-$(whoami)}
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
sudo /bin/chown $USER:$USER $AIMOA
sudo /bin/chown $USER:$USER $AIMOA/* -R
sudo /bin/chown $USER:$USER $AIMOA/.env/* -R -P 2>/dev/null
# Fix permissions so AI MOA can read-write
sudo /bin/chmod ug+rwx $AIMOA/config $AIMOA/logs $AIMOA/.env $AIMOA/app/input $AIMOA/app/output 2>/dev/null
sudo /bin/chmod ug+rw $AIMOA/config/* $AIMOA/logs/* $AIMOA/.env/* $AIMOA/app/input/* $AIMOA/app/output/* 2>/dev/null
sudo /bin/chmod ug+rw $AIMOA/llm-container/models -R
sudo /bin/chmod ug+rw $AIMOA/src/*.lock $AIMOA/config/*.lock 2>/dev/null
# Protect config.yaml from Other users
sudo /bin/chmod o-rwx $AIMOA/config $AIMOA/app $AIMOA/app/input $AIMOA/app/output 2>/dev/null

/bin/echo "Confirming current user belonging to the following groups (check for 'aimoa')..."
sudo /usr/bin/groups $USER
sudo /usr/bin/groups $USERNAME
/bin/echo ""
/bin/sleep 5s

# Protect installation files
sudo /bin/chmod guo+x $AIMOA/install/*
sudo /bin/chmod o-x $AIMOA/install/install*
sudo /bin/chmod o-x $AIMOA/install/uninstall*
# Protect config directory
sudo /bin/chmod o-rw ../config/config.yaml*

# Release file lock on workflow-config.yaml
# release_lock

# Reminder to add username to group aimoa
/bin/echo ""
/bin/echo "Remember to also add your username to "aimoa" group so your username can run AI-MOA...!"
/bin/echo "		(sudo usermod -a -G aimoa username)"
/bin/echo ""
/bin/echo "Please also check if 'aimoa' user or 'others' has r-x permissions from root directory / all the way to " $AIMOA
