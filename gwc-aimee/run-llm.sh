#!/bin/bash
# Startup script for local AI LLM Docker Containers
# Version 2024.12.09

CURRENT=$(pwd)
# CONFIGURATION:
# Automatic configuration of paths:
cd ..
AIMOA=$(pwd)
# Override by specifying the full path to AI-MOA base directory:
# AIMOA=/opt/ai-moa

# Confirm directory of installed AI-MOA:
/bin/echo "Currently specifying the following as the base directory for AI-MOA..."
/bin/echo $AIMOA

/bin/echo "This 'run-llm.sh' is for starting AI LLM Container by command line."
/bin/echo "You do not need to run this if you have installed AI LLM Container as a system service."
/bin/echo "	( Hint: To install AI LML Container as a system service, execute 'sudo ./install-llm.sh' )"
/bin/sleep 3s

# SPECIFY LLM Model to be used with AI-MOA:

# Option 1:
# Specify local GGUF LLM Model in local /models/ directory, use relative path:
export MODEL_NAME="$AIMOA/llm-container/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf"

# Option 2:
# Get Hugging Face LLM models directly from website, need to sign-in with Hugging Face user token to download models:
# export HF_TOKEN="{private_token}"
# export MODEL_NAME="RichardErkhov/Mistral-7B-Instruct-v0.3.Q8_0.gguf"
# export MODEL_NAME="microsoft/Phi-3.5-mini-instruct"

# Run AI LLM Containers:
# Note: Two containers will start, one for Aphrodite LLM container, the other is Caddy which operates the encrypted reverse proxy for SSL/TLS
# cd llm-container
# docker compose up -d
#
docker compose -f $AIMOA/llm-container/docker-compose.yml up -d

# Check LLM and Caddy docker containers running
/bin/sleep 3
docker ps -a

# Returning to previous path location
cd $CURRENT
