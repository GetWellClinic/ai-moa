#!/bin/bash
# Script to download and install default LLM Model
# Note: To correctly use automatic detection of AI-MOA path, this script must be reside and executed in AI-MOA subdirectory 'gwc-aimee'
# This script should be run as 'sudo ./install-model.sh'
# Version 2024.12.09

# CONFIGURATION:
# Using automatic detection, when this script is installed in AIMOA/gwc-aimee
cd ..
AIMOA=$(pwd)
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

# Specify the environmental variables for model name for use by LLM container and AI-MOA
/bin/echo "Using the following LLM model..."
/bin/echo $MODEL_NAME
# This environmental variable must be set before running AI-MOA
export MODEL_NAME="/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf”

# Fix permissions:
/bin/chown aimoa:aimoa $AIMOA/llm-container/models -R

# Note:
# You can download other AI models in GGUF format from Hugging Face and install them in models folder to use.
# Remember to specify the model name in AIMOA/src/config.yaml

