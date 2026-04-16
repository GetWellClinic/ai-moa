#!/bin/bash
# Script to download and install default LLM Model
# Note: To correctly use automatic detection of AI-MOA path, this script must be reside and executed in AI-MOA subdirectory 'gwc-aimee'
# This script should be run as 'sudo ./install-model.sh'
# Version 2025.02.02

# CONFIGURATION:
# Using automatic detection, when this script is found under directory "AIMOA/install/":
cd ..
AIMOA=$(pwd)
USER=${SUDO_USER:-$(whoami)}
# Override with specifying full path to AI-MOA installed directory:
# AIMOA=/opt/ai-moa

# Confirming base directory of AI-MOA:
/bin/echo "The followings has been specified as the base directory for AI-MOA..."
/bin/echo $AIMOA
/bin/echo ""
/bin/echo "...if this is incorrect, please press Crtl-C now to cancel installation now...!"
/bin/sleep 10s
/bin/echo ""

# Create AI-MOA/llm-container/models directory if not exist
/bin/echo "Creating models directory if not exist..."
/bin/mkdir $AIMOA/llm-container/models
cd $AIMOA/llm-container/models

# Download default AI-MOA model from Hugging Face to models directory
/bin/echo "Downloading default AI-MOA LLM model from Hugging Face..."
/bin/wget https://huggingface.co/RichardErkhov/mistralai_-_Mistral-7B-Instruct-v0.3-gguf/resolve/main/Mistral-7B-Instruct-v0.3.Q8_0.gguf -P $AIMOA/llm-container/models/

EXPECTED="3776268f275f5d448bfb6d14288ed858bde5502e63fc52b1f24fb30884b0d9a0"
FILE="$AIMOA/llm-container/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf"

CHECKSUM=$(sha256sum "$FILE" | awk '{print $1}')

if [ "$CHECKSUM" = "$EXPECTED" ]; then
    echo "Checksum verified!"
else
    echo "Checksum mismatch! File may be corrupted or tampered with. Please download again."
    exit 1
fi

# Specify the environmental variables for model name for use by LLM container and AI-MOA
/bin/echo "Using the following LLM model..."
# This environmental variable must be set before running AI-MOA
# Default: export MODEL_NAME="/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf"
export MODEL_NAME="/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf"
/bin/echo $MODEL_NAME

# Fix permissions:
sudo /bin/chown $USER:$USER $AIMOA/llm-container/models -R

# Note:
# You can download other AI models in GGUF format from Hugging Face and install them in models folder to use.
# Remember to specify the model name in AIMOA/src/config.yaml

