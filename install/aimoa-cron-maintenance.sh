#!/bin/bash
# This script periodically clears /tmp director of temporary Chrome/Chromium temp files
# and fixes permission to AI-MOA config files
# Version 2025.03.22
# Instructions: Edit and confirm location of AI-MOA install scripts; and then install this to crontab with "sudo crontab -e" to run periodically
# 0 6 * * * /opt/ai-moa/install/aimoa-cron-maintenance.sh

# CONFIG
# Files to delete older than how many days: (0.05 days is 1.2 hrs)
DAYS=0.05
# AI-MOA group user
GROUP=aimoa
# Path of AI-MOA (Please confirm/edit)
AIMOAPATH=/opt/ai-moa

# Change permission for user:group to AI-MOA group
/bin/echo "Fixing AI-MOA permissions..."
/bin/chown '$GROUP':'$GROUP' '$AIMOAPATH' -R
# Add read-write permissions to config files to fix permissions on *.yaml.lock files
/bin/chmod g+rw '$AIMOAPATH'/config/*

# Display files and timestamp
/bin/find /tmp -mtime $DAYS -type d -name '.com.google.Chrome*' -printf '%t\t%p\n'
/bin/find /tmp -mtime $DAYS -type d -name '.org.chromium.Chromium*' -printf '%t\t%p\n'

# Console instructions
/bin/echo ""
/bin/echo "The above files older than "$DAYS" days, will be deleted/cleared...please press Ctrl-C to cancel if desired..."
/bin/sleep 5s
/bin/echo ""

# Delete files older than $DAYS
/bin/echo "DELETING Chrome/Chromium /tmp files..."
/bin/sleep 2s
/bin/find /tmp -mtime $DAYS -type d -name '.com.google.Chrome*' -exec /bin/rm -rf '{}' \;
/bin/find /tmp -mtime $DAYS -type d -name '.org.chromium.Chromium*' -exec /bin/rm -rf '{}' \;

# Confirmation
/bin/echo ""
/bin/echo "/tmp files cleared older than "$DAYS" days."
/bin/echo ""
