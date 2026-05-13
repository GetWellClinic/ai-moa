#!/usr/bin/env bash

set -e

REPO_URL="https://github.com/mindee/doctr.git"
APP_DIR="/opt/doctr"
API_DIR="/opt/doctr/api"
CERT_DIR="/opt/doctr/api/certs"
PORT_MAPPING="8002:8080"

USER=${SUDO_USER:-$(whoami)}

install_git() {
    if ! command -v git >/dev/null 2>&1; then
        echo "[ERROR] Git is not installed."
        exit 1
    fi
}

install_openssl() {
    if ! command -v openssl >/dev/null 2>&1; then
        echo "OpenSSL not found. Installing..."

        sudo apt-get update
        sudo apt-get install -y openssl

        if ! command -v openssl >/dev/null 2>&1; then
            echo "[ERROR] Failed to install OpenSSL."
            exit 1
        fi

        echo "OpenSSL installed successfully: $(openssl version)"
    else
        echo "OpenSSL is already installed: $(openssl version)"
    fi
}

check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "[ERROR] Docker is not running or not installed."
        exit 1
    fi
}

clone_repo() {
    echo "Cloning DocTR repository..."

    sudo mkdir -p "$APP_DIR"
    sudo chown -R "$USER:$USER" "$APP_DIR"

    if [ -d "$APP_DIR/.git" ]; then
        echo "Repository already exists. Skipping clone."
    else
        cd "$APP_DIR"
        git clone "$REPO_URL" .
    fi
}

generate_ssl_cert() {
    echo "Generating self-signed SSL certificate..."

    mkdir -p "$CERT_DIR"

    if [ -f "$CERT_DIR/key.pem" ] && [ -f "$CERT_DIR/cert.pem" ]; then
        echo "SSL cert already exists. Skipping."
        return
    fi

    openssl req -x509 -newkey rsa:4096 \
        -keyout "$CERT_DIR/key.pem" \
        -out "$CERT_DIR/cert.pem" \
        -days 365 \
        -nodes \
        -subj "/CN=localhost"

    chmod 600 "$CERT_DIR/key.pem"
    chmod 644 "$CERT_DIR/cert.pem"

    echo "SSL certificate created at $CERT_DIR"
}

patch_docker_compose() {
    echo "Patching docker-compose.yml..."

    cd "$API_DIR"

    if [ ! -f docker-compose.yml ]; then
        echo "[ERROR] docker-compose.yml not found"
        exit 1
    fi

    if [ ! -f docker-compose.yml.bak ]; then
        cp docker-compose.yml docker-compose.yml.bak
        echo "Initial backup created."
    else
        echo "Backup already exists. Skipping."
    fi

    # If already patched, exit safely
    if grep -q "# BEGIN GPU BLOCK" docker-compose.yml; then
        echo "GPU block already exists. Skipping patch."
        return
    fi

    awk '

    /command: uvicorn/ {
        print "    command: uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8080 --ssl-keyfile /app/certs/key.pem --ssl-certfile /app/certs/cert.pem"
        next
    }
    
    /ports:/ {
        print $0
        getline

        gsub(/8080:8080/, "8002:8080")
        print $0

        print "    # BEGIN GPU BLOCK"
        print "    runtime: nvidia"
        print "    environment:"
        print "      - NVIDIA_VISIBLE_DEVICES=all"
        print "    volumes:"
        print "      - ./certs:/app/certs"
        print "    # END GPU BLOCK"

        next
    }

    { print }

    ' docker-compose.yml > docker-compose.tmp

    mv docker-compose.tmp docker-compose.yml

    echo "docker-compose.yml updated successfully."
}

verify_gpu_docker() {
    echo "Testing GPU Docker access..."

    docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi || {
        echo "[ERROR] GPU Docker test failed."
        exit 1
    }
}

run_make() {
    echo "Running make run..."

    cd "$API_DIR"

    if command -v make >/dev/null 2>&1; then
        make run
    else
        echo "[ERROR] make not installed."
        exit 1
    fi
}

main() {
    echo "Starting doctr ocr api..."

    install_git
    check_docker
    install_openssl
    clone_repo
    generate_ssl_cert
    patch_docker_compose
    verify_gpu_docker
    run_make

    echo "Deployment complete!"
    echo "API available at: https://localhost:8002"
}

main "$@"