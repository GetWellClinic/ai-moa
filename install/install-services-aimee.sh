#!/bin/bash
# This script helps you install llm-container and the full set of Aimee-AI as a system service running automatically on Linux boot.
# This script should reside and be run in the AI-MOA subdirectory 'install' in order to properly autodetect base directory for AI-MOA.
# Run the script as 'sudo ./install-services-aimee.sh'

# Version 2025.06.09

# Aimee AI services require minimum 16 GB VRAM GPU to run multiple ai-moa services:
#	llm-container
#	ai-moa.service
#	ai-moa-incomingfax.service
#	ai-moa-incomfingfile.service

# Automatic detect base directory for AI-MOA:
cd ..
AIMOA=$(pwd)
# Override to specify base directory for AI-MOA:
# AIMOA=/opt/ai-moa

/bin/echo "Installing Aimee AI services for 'ai-moa.service', 'ai-moa-incomingfax.service', 'ai-moa-incomingfile.service', and 'llm-container' to autostart on system reboot..."
/bin/echo ""
/bin/echo "NOTICE: This full Aimee AI installation requires minimum 16 GB VRAM GPU !"
/bin/echo ""

# Confirm base directory:
/bin/echo "Please confirm the correct base directory for AI-MOA as shown below..."
/bin/echo $AIMOA
/bin/echo ""
/bin/echo "...if this is incorrect, please press Ctrl-C to cancel installation...!"
/bin/sleep 10s

# Edit the AI-MOA services to match installed AI-MOA base directory:
/bin/cp $AIMOA/install/services/ai-moa.service.default $AIMOA/install/services/ai-moa.service
/bin/cp $AIMOA/install/services/ai-moa-incomingfax.service.default $AIMOA/install/services/ai-moa-incomingfax.service
/bin/cp $AIMOA/install/services/ai-moa-incomingfile.service.default $AIMOA/install/services/ai-moa-incomingfile.service
/bin/cp $AIMOA/install/services/llm-container.service.default $AIMOA/install/services/llm-container.service
/bin/sed -i 's#/opt/ai-moa#'"$AIMOA"'#g' $AIMOA/install/services/ai-moa.service
/bin/sed -i 's#/opt/ai-moa#'"$AIMOA"'#g' $AIMOA/install/services/ai-moa-incomingfax.service
/bin/sed -i 's#/opt/ai-moa#'"$AIMOA"'#g' $AIMOA/install/services/ai-moa-incomingfile.service
/bin/sed -i 's#/opt/ai-moa#'"$AIMOA"'#g' $AIMOA/install/services/llm-container.service

# Install AI-MOA and LLM Container as system services in Linux:
/bin/cp $AIMOA/install/services/ai-moa.service /etc/systemd/system/
/bin/cp $AIMOA/install/services/ai-moa-incomingfax.service /etc/systemd/system/
/bin/cp $AIMOA/install/services/ai-moa-incomingfile.service /etc/systemd/system/
/bin/cp $AIMOA/install/services/llm-container.service /etc/systemd/system/
# Reload any changes to system service folder /etc/systemd/system
/usr/bin/systemctl daemon-reload

# Enable system AI-MOA and LLM Container services:
/usr/bin/systemctl enable ai-moa.service
/usr/bin/systemctl enable ai-moa-incomingfax.service
/usr/bin/systemctl enable ai-moa-incomingfile.service
/usr/bin/systemctl enable llm-container.service
# Start system services:
/usr/sbin/service llm-container start
/usr/sbin/service ai-moa start
/usr/sbin/service ai-moa-incomingfax start
/usr/sbin/service ai-moa-incomingfile start

# Install crontab for Sunday morning reboot (to autofix kernel unattended upgrades mismatch with NVIDIA drivers causing AI-MOA to halt)
 REBOOTCRON="1 4 * * SUN     /usr/sbin/shutdown -r now"
# Check if already exists, and add if not exist:
if sudo crontab -u root -l 2>/dev/null | /bin/grep -Fq "$REBOOTCRON"; then
	/bin/echo "Cron job already exists. Skipping adding reboot job...Please verify correct installation of existing cron job...!"
else
	(sudo crontab -u root -l && /bin/echo "# AI-MOA Cronjob for weekly reboot, to autofix halted AI-MOA due to unattended kernel and NVIDIA drivers upgrade" 2>/dev/null) | sudo crontab -
	(sudo crontab -u root -l && /bin/echo "$REBOOTCRON" 2>/dev/null) | sudo crontab -
	/bin/echo "Added Sunday weekly reboot to sudo crontab...successful."
fi

/bin/echo "ai-moa.service, ai-moa-incomingfax.service, ai-moa-incomingfile.service and llm-container.service has been installed as system services in /etc/systemd/system/"
/bin/echo "Aimee AI will start automatically on system reboot !"
/bin/echo ""
# To stop services temporarily: 'sudo system ai-moa stop' , 'sudo system ai-moa-incomingfax stop', 'sudo system llm-container stop'

/bin/echo "	Tips:"
/bin/echo "		to stop AI-MOA 'sudo system ai-moa stop', 'sudo system ai-moa-incomingfax stop', and 'sudo system ai-moa-incomingfile stop'"
/bin/echo "		to start AI-MOA 'sudo system ai-moa start', 'sudo system ai-moa-incomingfax start', and 'sudo system ai-moa-incomingfile start'"
/bin/echo "		to check NVIDIA GPU 'nvidia-smi'"
/bin/echo "		to disable AI-MOA from restarting on reboot 'sudo systemctl disable ai-moa.service', 'sudo systemctl disable ai-moa-incomingfax.service', and 'sudo systemctl disable ai-moa-incomingfax.service'"
/bin/echo "		to re-enable AI-MOA to restart automatically on reboot 'sudo systemctl enable ai-moa.service', 'sudo systemctl enable ai-moa-incomingfax.service', and 'sudo systemctl enable ai-moa-incomingfile.service'"
/bin/echo ""

# To disable system services, and prevent from restarting on reboot: 'sudo systemctl disable ai-moa.service' , 'sudo systemctl disable ai-moa-incomingfax.service', 'sudo systemctl disable ai-moa-incomingfile.service', 'sudo systemctl disable llm-container.service'
