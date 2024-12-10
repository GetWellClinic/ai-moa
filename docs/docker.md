# Installing Docker and Docker Compose

This guide will walk you through the process of installing **Docker** and **Docker Compose** on Ubuntu. 

## Steps to Install Docker

To install Docker on Ubuntu, follow the official Docker documentation guide:

- Official Docker installation instructions for Ubuntu: [Docker Installation on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

Once Docker is installed, you can verify the installation by running:

`docker --version`

## Steps to Install Docker Compose

### 1. Install Docker Compose using pip

You can install Docker Compose via Python's package manager, pip, with the following command:

`pip install docker-compose`

After installation, verify Docker Compose is installed successfully by running:

`docker-compose --version`

### 2. If pip installation fails

If you encounter issues using pip, you can manually install Docker Compose by following the steps below:

Download Docker Compose:

Run the following curl command to download Docker Compose from GitHub:

`sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`

Make Docker Compose executable:

After downloading, make the docker-compose binary executable by running:

`sudo chmod +x /usr/local/bin/docker-compose`

Verify Docker Compose installation:

Finally, verify that Docker Compose is installed by running:

`docker-compose --version`
