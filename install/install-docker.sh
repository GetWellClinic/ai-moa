#!/bin/bash
# This script helps you install Docker, Docker Compose, and Python pip
# This script should be run as 'sudo ./install-docker.sh'
# Version 2025.04.27

CURRENT=$(pwd)

# Change to home directory
cd ~/

# apt-get update
# apt-get install ubuntu-drivers-common
# ubuntu-drivers devices
# apt install nvidia-driver-550
# Need to reboot server, for installation to take effect and see the NVIDIA RTX working:
# nvidia-smi

# Install Docker:

# Install Docker repository GPG key to keyring:
/bin/curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc

# Add Docker repository to Apt resources:
/bin/echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update

# Install latest Docker
apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Can confirm docker running by testing hello-world docker:
# docker run hello-world

# Install Python pip package manager if not installed
apt-get -y install python3-pip

# Install Docker Compose
apt-get -y install docker-compose
pip install docker-compose
# Hint: New Docker Compose command has no space, ie. 'docker compose'

# Confirm Docker Version
docker --version

# Install NVIDIA Container Toolkit:
#
# ** This needs to be installed before running the next part of the script. Check readme.md **
#
# curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
# 	&& curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
#	sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
#	sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
#
# apt-get update
# apt-get install nvidia-container-toolkit
#
# ** Restart the server for installation to take effect and continue (ie. shutdown -r now) **

# Configure Docker to use NVIDIA Container Toolkit
/bin/echo "Configuring Docker to use NVIDIA Container Toolkit"
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

# Go back to previous path location
cd $CURRENT
