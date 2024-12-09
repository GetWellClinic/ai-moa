#!/bin/bash
# Shutdown script for local AI LLM Docker Containers
# Version 2024.12.09

# CONFIGURATION:
# Automatic detection of base directory for AI-MOA:
cd ..
AIMOA=$(pwd)
# Override by specifying full path to AI-MOA base directory:
# AIMOA=/opt/ai-moa

# Confirm base directory for AI-MOA:
/bin/echo "Specifying AI-MOA base directory..."
/bin/echo $AIMOA

# SPECIFY LLM MODEL:
#
# Option 1:
# Specify local GGUF LLM Model in local llm-container/models/ directory:
export MODEL_NAME="$AIMOA/llm-container/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf"

# Option 2:
# Get Hugging Face LLM models directly from website, need to sign-in with Hugging Face user token to download models:
# export HF_TOKEN="{private_token}"
# export MODEL_NAME="Mistral-7B-Instruct-v0.3.Q8_0.gguf"
# export MODEL_NAME="microsoft/Phi-3.5-mini-instruct"

# Run AI LLM Containers:
# Note: Two containers will start, one for Aphrodite LLM container, the other is Caddy which operates the encrypted reverse proxy for SSL/TLS
# cd llm-container
# docker compose down -d
#
/bin/echo "Halting AI LLM Containers..."
docker compose -f $AIMOA/llm-container/docker-compose.yml down

# Check LLM and Caddy docker containers running
/bin/sleep 3
docker ps -a
