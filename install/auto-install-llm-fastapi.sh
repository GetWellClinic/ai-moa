#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/ai-moa"
LLM_CONTAINER_DIR="$APP_DIR/llm-container"
MODELS_DIR="$LLM_CONTAINER_DIR/models"

AIMOA_USER="aimoa"

MODEL_URL="https://huggingface.co/RichardErkhov/mistralai_-_Mistral-7B-Instruct-v0.3-gguf/resolve/main/Mistral-7B-Instruct-v0.3.Q8_0.gguf"
MODEL_FILE="Mistral-7B-Instruct-v0.3.Q8_0.gguf"

EXPECTED_SHA256="3776268f275f5d448bfb6d14288ed858bde5502e63fc52b1f24fb30884b0d9a0"


check_aimoa_user() {
    echo "Checking if user '$AIMOA_USER' exists..."

    if ! id "$AIMOA_USER" >/dev/null 2>&1; then
        echo "[ERROR] User '$AIMOA_USER' does not exist."
        exit 1
    fi

    echo "User '$AIMOA_USER' found."
}


run_as_aimoa() {

sudo -u "$AIMOA_USER" bash <<EOF
set -euo pipefail

APP_DIR="$APP_DIR"
LLM_CONTAINER_DIR="$LLM_CONTAINER_DIR"
MODELS_DIR="$MODELS_DIR"

MODEL_URL="$MODEL_URL"
MODEL_FILE="$MODEL_FILE"
EXPECTED_SHA256="$EXPECTED_SHA256"

/bin/echo "The base directory for the AI-MOA installation is: \$APP_DIR"
/bin/echo "Press Ctrl-C within 5 seconds to cancel if this is the incorrect location."
/bin/sleep 10s

# Validate paths
if [ ! -d "\$APP_DIR" ]; then
    echo "[ERROR] Missing \$APP_DIR"
    exit 1
fi

if [ ! -d "\$LLM_CONTAINER_DIR" ]; then
    echo "[ERROR] Missing \$LLM_CONTAINER_DIR"
    exit 1
fi

# Create models dir
mkdir -p "\$MODELS_DIR"
cd "\$MODELS_DIR"

MODEL_PATH="\$MODELS_DIR/\$MODEL_FILE"

# Download model
if [ -f "\$MODEL_PATH" ]; then
    echo "Model already exists"
else
    echo "Downloading model..."
    wget "\$MODEL_URL" -O "\$MODEL_PATH"
fi

# Verify checksum
echo "Verifying checksum..."
CHECKSUM=\$(sha256sum "\$MODEL_PATH" | awk '{print \$1}')

if [ "\$CHECKSUM" != "\$EXPECTED_SHA256" ]; then
    echo "[ERROR] Checksum mismatch"
    exit 1
fi

echo "Checksum verified"

# Patch docker-compose
DOCKER_COMPOSE_FILE="\$LLM_CONTAINER_DIR/docker-compose.yml"

if [ ! -f "\$DOCKER_COMPOSE_FILE" ]; then
    echo "[ERROR] docker-compose.yml missing"
    exit 1
fi

if [ ! -f "\${DOCKER_COMPOSE_FILE}.bak" ]; then
    cp "\$DOCKER_COMPOSE_FILE" "\${DOCKER_COMPOSE_FILE}.bak"
fi

sed -i \
's|MODEL_NAME=.*gemma-2-2b-it}|MODEL_NAME=\${MODEL_NAME:-/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf}|g' \
"\$DOCKER_COMPOSE_FILE"

sed -i \
's|--model .*gemma-2-2b-it}|--model \${MODEL_NAME:-/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf}|g' \
"\$DOCKER_COMPOSE_FILE"

echo "docker-compose file updated"
EOF

}


main() {
    echo "Starting AI-MOA setup..."
    check_aimoa_user
    run_as_aimoa

    echo "Starting containers..."
    cd "$LLM_CONTAINER_DIR"
    docker compose up -d

    echo "Done."
}

main "$@"