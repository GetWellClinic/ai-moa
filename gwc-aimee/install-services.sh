#!/bin/bash
# This script helps you install llm-container and ai-moa as a system service running automatically on Linux boot.
# This script should reside and be run in the AI-MOA subdirectory 'gwc-aimee' in order to properly autodetect base directory for AI-MOA.
# Run the script as 'sudo ./install-services.sh'

# Version 2024.12.09

# Automatic detect base directory for AI-MOA:
cd ..
AIMOA=$(pwd)
# Override to specify base directory for AI-MOA:
# AIMOA=/opt/ai-moa

# Confirm base directory:
/bin/echo "Please confirm the correct base directory for AI-MOA as shown below..."
/bin/echo $AIMOA
/bin/echo ""
/bin/echo "...if this is incorrect, please press Ctrl-C to cancel installation...!"
/bin/sleep 10s

# Edit the AI-MOA services to match installed AI-MOA base directory:
/bin/cp $AIMOA/gwc-aimee/services/ai-moa.service.default $AIMOA/gwc-aimee/services/ai-moa.service
/bin/cp $AIMOA/gwc-aimee/services/llm-container.service.default $AIMOA/gwc-aimee/services/llm-container.service
/bin/sed -i 's#/opt/ai-moa#'"$AIMOA"'#g' $AIMOA/gwc-aimee/services/ai-moa.service
/bin/sed -i 's#/opt/ai-moa#'"$AIMOA"'#g' $AIMOA/gwc-aimee/services/llm-container.service

# Install AI-MOA and LLM Container as system services in Linux:
/bin/cp $AIMOA/gwc-aimee/services/ai-moa.service /etc/systemd/system/
/bin/cp $AIMOA/gwc-aimee/services/llm-container.service /etc/systemd/system/
# Reload any changes to system service folder /etc/systemd/system
/usr/bin/systemctl daemon-reload

# Enable system AI-MOA and LLM Container services:
/usr/bin/systemctl enable ai-moa.service
/usr/bin/systemctl enable llm-container.service
# Start system services:
/usr/sbin/service llm-container start
/usr/sbin/service ai-moa start

/bin/echo "ai-moa.service and llm-container.service has been installed as system services in /etc/systemd/system/"
/bin/echo "AI-MOA will start automatically on system reboot !"
/bin/echo ""
# To stop services temporarily: 'sudo system ai-moa stop' , 'sudo system llm-container stop'
/bin/echo "	Tips:"
/bin/echo "		to stop AI-MOA 'sudo system ai-moa stop'"
/bin/echo "		to start AI-MOA 'sudo system ai-moa start'"
/bin/echo "		to check NVIDIA GPU 'nvidia-smi'"
/bin/echo "		to disable AI-MOA from restarting on reboot 'sudo systemctl disable ai-moa.service'"
/bin/echo "		to re-enable AI-MOA to restart automatically on reboot 'sudo systemctl enable ai-moa.service'"
/bin/echo ""

# To disable system services, and prevent from restarting on reboot: 'sudo systemctl disable ai-moa.service' , 'sudo systemctl disable llm-container.service'
