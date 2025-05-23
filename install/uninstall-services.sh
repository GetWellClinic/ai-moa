#!/bin/bash
# This script helps you REMOVE / uninstall llm-container and ai-moa system services
# This script should be edited first to confirm correct base directory for AI-MOA
# Run the script as 'sudo ./uninstall-services.sh'
# Version 2025.03.26

# Automatic detect base directory for AI-MOA:
cd ..
AIMOA=$(pwd)

# Confirm base directory:
/bin/echo "Please confirm the correct base directory for AI-MOA as shown below..."
/bin/echo $AIMOA
/bin/echo ""
/bin/echo "...if this is incorrect, please press Ctrl-C to cancel installation...!"
/bin/sleep 10s

# Stopping services:
/usr/sbin/service llm-container stop
/usr/sbin/service ai-moa stop
/usr/sbin/service ai-moa-incomingfax stop
/usr/sbin/service ai-moa-incomingfile stop
# Disable system services:
/usr/bin/systemctl disable ai-moa.service
/usr/bin/systemctl disable ai-moa-incomingfax.service
/usr/bin/systemctl disable ai-moa-incomingfile.service
/usr/bin/systemctl disable llm-container.service

# REMOVE/Uninstall AI-MOA and LLM Container as system services in Linux:
/bin/mv /etc/systemd/system/ai-moa.service $AIMOA/install/services/ai-moa.service.removed
/bin/mv /etc/systemd/system/ai-moa-incomingfax.service $AIMOA/install/services/ai-moa-incomingfax.service.removed
/bin/mv /etc/systemd/system/ai-moa-incomingfile.service $AIMOA/install/services/ai-moa-incomingfile.service.removed
/bin/mv /etc/systemd/system/llm-container.service $AIMOA/install/services/llm-container.service.removed
/bin/echo "ai-moa and llm-container services removed from /etc/systemd/system/ and moved to $AIMOA/install/services/*.services.removed"
# Reload any changes to system service folder /etc/systemd/system
/usr/bin/systemctl daemon-reload
/bin/echo ""
/bin/echo "AI-MOA and LLM Container removed as system services."
