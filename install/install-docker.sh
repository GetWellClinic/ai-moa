#!/bin/bash

set -e

CURRENT_USER=${SUDO_USER:-$(whoami)}

check_docker() {
    command -v docker >/dev/null 2>&1
}

if check_docker; then
    echo "Docker is already installed: $(docker --version)"
    echo "Skipping Docker installation."
else
    echo "Docker not found, installing..."

    echo "Updating system..."
    sudo apt-get update

    echo "Installing dependencies..."
    sudo apt-get install -y ca-certificates curl gnupg lsb-release

    echo "Setting up Docker repository..."

    sudo install -m 0755 -d /etc/apt/keyrings

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update

    echo "Installing Docker..."
    sudo apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    echo "Enabling Docker service..."
    sudo systemctl enable docker
    sudo systemctl start docker

    echo "Adding current user to docker group..."
    sudo usermod -aG docker "$CURRENT_USER"

    echo ""
    echo "Docker installation completed."
    echo "You must log out and log back in for Docker group changes to take effect."
fi

echo ""
echo "Docker Version:"
docker --version || true

echo ""
echo "Docker Compose Version:"
docker compose version || true

echo ""
echo "Installation script completed."