#!/usr/bin/env bash
# COPYRIGHT © 2026 by Spring Health Corporation <office(at)springhealth.org>
# Toronto, Ontario, Canada
# SUMMARY: This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software,
# documentation, and configuration files.
# These programs, documentation, and configuration files are made available to you as open source
# in the hopes that your clinic or organization may find it useful and improve your care to the public
# by reducing administrative burden for your staff and service providers.
# NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
# and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
# LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
# Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.
# ***
# NOTICE: We hope that you will consider contributing to our common source code repository so that
# others may benefit from your shared work.
# However, if you distribute this code or serve this application to users in modified form,
# or as part of a derivative work, you are required to make your modified or derivative work
# source code available under the same herein described license.
# Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work
# source code can be acquired publicly in its latest most up-to-date version, within one month.
# ***
set -e

USER=${SUDO_USER:-$(whoami)}

REQUIRED_CUDA="12.4"
REQUIRED_DRIVER="550"
REQUIRED_PYTHON="3.10"
APP_USER="aimoa"
APP_DIR="/opt/ai-moa"
AIMOA_PY_ENV_DIR="/opt/ai-moa.env"

version_ge() {
    # Returns 0 if $1 >= $2
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

check_cuda() {
    if ! command -v nvidia-smi >/dev/null 2>&1; then
        return 1
    fi

    CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
    DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n1)

    echo "Detected Driver Version: $DRIVER_VERSION"
    echo "Detected CUDA Version: $CUDA_VERSION"

    [[ -n "$CUDA_VERSION" ]] || return 1

    version_ge "$CUDA_VERSION" "$REQUIRED_CUDA" || return 1
    version_ge "$DRIVER_VERSION" "$REQUIRED_DRIVER" || return 1

    return 0
}

check_docker() {
    if command -v docker >/dev/null 2>&1; then
        echo "Docker is already installed: $(docker --version)"
        return 0
    else
        return 1
    fi
}

setup_aimoa_user() {
    if id "$APP_USER" >/dev/null 2>&1; then
        echo "User $APP_USER already exists. Skipping user creation."
    else
        sudo useradd -m -s /bin/bash "$APP_USER"
    fi
}

setup_repo() {
    install_git

    sudo mkdir -p "$APP_DIR"
    sudo mkdir -p "$AIMOA_PY_ENV_DIR"
    sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    sudo chown -R "$APP_USER:$APP_USER" "$AIMOA_PY_ENV_DIR"

    if [ -d "$APP_DIR/.git" ]; then
        echo "Repository already exists at $APP_DIR. Skipping clone."
        return
    fi

    echo "Setting up application and env directory..."

    sudo -u "$APP_USER" bash <<EOF
set -e
cd "$APP_DIR"
git clone https://github.com/GetWellClinic/ai-moa.git .
cd install
ls -l -h
chmod ug+x *.sh
chmod g-x install* uninstall* || true
EOF
}

setup_aimoa_directories() {
    echo "Setting up AI-MOA directories and config files..."

    sudo -u "$APP_USER" bash <<EOF
set -e

echo "Creating log directory..."
mkdir -p "$APP_DIR/logs"

echo "Creating config directory..."
mkdir -p "$APP_DIR/config"

echo "Creating app directories..."
mkdir -p "$APP_DIR/app"
mkdir -p "$APP_DIR/app/input"
mkdir -p "$APP_DIR/app/output"

echo "Creating llm-container/models directory..."
mkdir -p "$APP_DIR/llm-container/models"

echo "Creating config files from templates..."

if [ ! -f "$APP_DIR/config/config.yaml" ]; then
    cp "$APP_DIR/src/config.yaml.example" \
       "$APP_DIR/config/config.yaml"
fi

if [ ! -f "$APP_DIR/config/workflow-config.yaml" ]; then
    cp "$APP_DIR/src/workflow-config.yaml.example" \
       "$APP_DIR/config/workflow-config.yaml"
fi

if [ ! -f "$APP_DIR/config/template_providerlist.txt" ]; then
    cp "$APP_DIR/src/template_providerlist.txt" \
       "$APP_DIR/config/template_providerlist.txt"
fi

EOF

    echo "AI-MOA directory setup complete."
}

install_git() {
    if ! command -v git >/dev/null 2>&1; then
        echo "Git not found. Installing..."
        sudo apt-get update
        sudo apt-get install -y git
    else
        echo "Git is already installed: $(git --version)"
    fi
}

install_chrome() {
    if ! command -v google-chrome >/dev/null 2>&1; then
        echo "Google Chrome not found. Installing..."

        sudo apt-get update
        sudo apt-get install -y wget gnupg

        # Add Google Chrome repository
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
            sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg

        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
            sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null

        # Install Chrome
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable

        echo "Google Chrome installed successfully."
    else
        echo "Google Chrome is already installed: $(google-chrome --version)"
    fi
}

install_driver() {
    echo "Installing NVIDIA driver branch >= ${REQUIRED_DRIVER}..."
    sudo apt update

    if dpkg -l | grep -q "nvidia-driver-${REQUIRED_DRIVER}"; then
        echo "Driver already installed."
    else
        sudo apt install -y "nvidia-driver-${REQUIRED_DRIVER}"
    fi
}

install_nvidia_container_toolkit() {

    echo "Adding NVIDIA Container Toolkit repository and GPG key..."

    if [ ! -f /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg ]; then
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
        sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    fi

    if [ ! -f /etc/apt/sources.list.d/nvidia-container-toolkit.list ]; then
        curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
    fi

    echo "Updating package list..."
    sudo apt-get update

    echo "Installing NVIDIA Container Toolkit..."
    sudo apt-get install -y nvidia-container-toolkit

    echo "NVIDIA Container Toolkit installation complete."

    if check_docker; then
        echo "Skipping Docker installation."
    else
        echo "Docker not found, installing..."
        
        echo "Updating system..."
        sudo apt-get update

        echo "Installing dependencies..."
        sudo apt-get install -y ca-certificates curl gnupg

        echo "Setting up Docker repository..."

        sudo install -m 0755 -d /etc/apt/keyrings

        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
            sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
            sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        sudo apt-get update
        echo "Installing Docker..."
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

        sudo systemctl enable docker
        sudo systemctl start docker

        echo "Adding user to docker group..."
        # Add the invoking admin user to the docker group so they can manage containers.
        # Note: The aimoa account is intentionally *not* added here to avoid
        # granting root-equivalent Docker socket access to the app user.
        sudo usermod -aG docker "$USER"
        
        echo "You must log out and log back in for Docker group changes to take effect."

        echo "After logging back in, please rerun this script again to complete installation."
        sleep 5

    fi

    echo "Configuring Docker runtime..."
    sudo nvidia-ctk runtime configure --runtime=docker

    echo "Restarting Docker..."
    sudo systemctl restart docker

}

detect_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON=python3
    elif command -v python >/dev/null 2>&1; then
        PYTHON=python
    else
        PYTHON=""
    fi
}

install_python_virtualenv() {
    detect_python

    if [[ -z "$PYTHON" ]]; then
        echo "Python not found. Installing python3..."
        sudo apt-get update
        sudo apt-get install -y python3
        PYTHON=python3
    else
        echo "Detected Python: $($PYTHON --version)"
    fi

    # Install pip if not already installed
    if ! command -v pip3 >/dev/null 2>&1; then
        sudo apt-get install -y python3-pip
    else
        echo "pip3 is already installed: $(pip3 --version)"
    fi

    # Install virtualenv
    if ! command -v virtualenv >/dev/null 2>&1; then
        sudo apt-get install -y python3-virtualenv
    else
        echo "virtualenv is already installed: $(virtualenv --version)"
    fi

    echo "Python 3 and virtualenv installation complete."
}

verify_docker_gpu() {
    echo "Testing Docker GPU access..."

    if ! docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi; then
        echo "GPU Docker test failed"
        echo "You must log out and log back in for Docker group changes to take effect."
        echo "After that rerun this script."
        exit 1
    fi
}

verify_installation() {
    echo
    echo "=== Verifying Installation ==="

    all_ok=true

    if command -v nvidia-smi >/dev/null 2>&1; then
        CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
        DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n1)

        if version_ge "$CUDA_VERSION" "$REQUIRED_CUDA" && version_ge "$DRIVER_VERSION" "$REQUIRED_DRIVER"; then
            echo "[x] NVIDIA driver ($DRIVER_VERSION) and CUDA ($CUDA_VERSION) meet requirements"
        else
            echo "[ ] NVIDIA driver ($DRIVER_VERSION) or CUDA ($CUDA_VERSION) too low"
            all_ok=false
        fi
    else
        echo "[ ] NVIDIA driver not installed or nvidia-smi not found"
        all_ok=false
    fi

    if dpkg -l | grep -q nvidia-container-toolkit; then
        echo "[x] NVIDIA Container Toolkit installed"
    else
        echo "[ ] NVIDIA Container Toolkit not installed"
        all_ok=false
    fi

    if command -v docker >/dev/null 2>&1; then
        echo "[x] Docker installed: $(docker --version)"
    else
        echo "[ ] Docker not installed"
        all_ok=false
    fi

    if command -v git >/dev/null 2>&1; then
        echo "[x] Git installed: $(git --version)"
    else
        echo "[ ] Git not installed"
        all_ok=false
    fi

    if command -v python3 >/dev/null 2>&1; then
        PYTHON=python3
    elif command -v python >/dev/null 2>&1; then
        PYTHON=python
    else
        PYTHON=""
    fi

    if [[ -z "$PYTHON" ]]; then
        echo "[ ] Python not found. Please install Python >= $REQUIRED_PYTHON"
        all_ok=false
    else
        PYTHON_VERSION=$($PYTHON -c 'import sys; print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')
        if [ "$(printf '%s\n' "$PYTHON_VERSION" "$REQUIRED_PYTHON" | sort -V | head -n1)" = "$REQUIRED_PYTHON" ]; then
            echo "[x] $PYTHON version $PYTHON_VERSION meets requirement >= $REQUIRED_PYTHON"
        else
            echo "[ ] $PYTHON version $PYTHON_VERSION is less than required $REQUIRED_PYTHON"
            all_ok=false
        fi
    fi

    if [[ -n "$PYTHON" ]]; then
        if ! $PYTHON -m pip --version >/dev/null 2>&1; then
            echo "[ ] pip not installed for $PYTHON"
            all_ok=false
        else
            PIP_VERSION=$($PYTHON -m pip --version | awk '{print $2}')
            echo "[x] pip found for $PYTHON: version $PIP_VERSION"
        fi
    fi

    if ! command -v virtualenv >/dev/null 2>&1; then
        echo "[ ] virtualenv not installed"
        all_ok=false
    else
        echo "[x] virtualenv found: $(virtualenv --version)"
    fi

    if id "$APP_USER" >/dev/null 2>&1; then
        echo "[x] AI-MOA user exists: $APP_USER"
    else
        echo "[ ] AI-MOA user $APP_USER missing"
        all_ok=false
    fi

    if [ -d "$APP_DIR/.git" ]; then
        echo "[x] AI-MOA directory exists at $APP_DIR"
    else
        echo "[ ] AI-MOA directory not found at $APP_DIR"
        all_ok=false
    fi

    if command -v google-chrome >/dev/null 2>&1; then
        echo "[x] Google Chrome installed successfully: $(google-chrome --version)"
    else
        echo "[ ] Google Chrome installation failed"
        all_ok=false
    fi

    echo
    if $all_ok; then
        echo "** All requirements installed successfully! **"
    else
        echo "**  Some requirements are missing. Please review the checklist above. **"
    fi
    echo "=== Verification Complete ==="
    echo

    if $all_ok; then

        echo "Setting up Python virtual environment and installing requirements..."

        sudo -u "$APP_USER" bash <<EOF
if [ ! -d "$AIMOA_PY_ENV_DIR/pyenv" ]; then
    $PYTHON -m virtualenv "$AIMOA_PY_ENV_DIR/pyenv"
fi

source "$AIMOA_PY_ENV_DIR/pyenv/bin/activate"

pip install --upgrade pip

if [ -f "$APP_DIR/src/requirements.txt" ]; then
    pip install -r "$APP_DIR/src/requirements.txt"
else
    echo "Warning: requirements.txt not found at $APP_DIR/src/requirements.txt"
fi
EOF
        echo
        echo "Python environment ($AIMOA_PY_ENV_DIR/pyenv) setup complete."
        echo

        echo "This installer script can be found at $APP_DIR/install/auto-install-aimoa.sh"
        echo "Removing installer script which was downloaded at the beginning..."
        rm -- "$0" || echo "Could not remove the script automatically."

        echo
        echo "Use the Config file at $APP_DIR/config/config.yaml to update your configuration"
        echo
        echo "Use the Workflow config file at $APP_DIR/config/workflow-config.yaml to update your workflow configuration"
    fi
}

main() {
    echo "Checking existing NVIDIA installation..."

    if check_cuda; then
        echo "Compatible NVIDIA system detected."
        install_nvidia_container_toolkit
        verify_docker_gpu
        install_python_virtualenv
        setup_aimoa_user
        setup_repo
        setup_aimoa_directories
        install_chrome
        verify_installation
    else

        echo
        echo "NVIDIA driver or CUDA requirement not satisfied."
        echo

        echo "Choose installation method:"
        echo "1) Let this script install NVIDIA driver branch >= ${REQUIRED_DRIVER}"
        echo "2) I will install manually"
        echo

        read -p "Enter choice [1/2]: " choice

        case "$choice" in
            1)
                install_driver
                
                echo
                echo "Installation complete. Reboot required."
                echo

                read -p "Reboot now? [Y/N]: " ans
                if [[ "$ans" =~ ^[Yy]$ ]]; then
                    echo "After reboot, please rerun this script again to complete installation."
                    echo "Rebooting in 5 seconds..."
                    sleep 5
                    sudo reboot
                else
                    echo "Please reboot manually and rerun the script."
                fi
                ;;
            2)
                echo
                echo "Please install NVIDIA driver ${REQUIRED_DRIVER} or greater manually."
                echo "Then reboot and rerun this script."
                exit 0
                ;;
            *)
                echo "Invalid option. Exiting."
                exit 1
                ;;
        esac
    fi
}

main "$@"