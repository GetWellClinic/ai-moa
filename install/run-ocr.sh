#!/bin/bash
# Startup script for local OCR Docker Container
# Version 2025.05.10

CURRENT=$(pwd)
# CONFIGURATION:
# Automatic configuration of paths:
cd ..
AIMOA=$(pwd)
# Override by specifying the full path to AI-MOA base directory:
# AIMOA=/opt/ai-moa
OCRAPI=/opt/doctr

# Confirm directory of installed AI-MOA:
/bin/echo "Currently specifying the following as the base directory for AI-MOA..."
/bin/echo $AIMOA

/bin/echo "This 'run-ocr.sh' is for starting OCR Container by command line."
/bin/echo "You do not need to run this if you run this as a system service."
/bin/echo "	( Hint: To install OCR Container as a system service, execute 'sudo ./install-ocr.sh' )"
/bin/echo ""
/bin/echo "Note: The first document you process with AI-MOA with extract_text_doctr_api will take a longer time as"
/bin/echo "the system downloads the OCR models. The subsequent document OCR process will be alot quicker running"
/bin/echo "on the GPU. You can check if the OCR model was loaded in to GPU with nvidia-smi and compare GPU usage"
/bin/echo "before and after."
/bin/sleep 3s

# Run OCR Containers:
# Note: Two containers will start, one for OCR container, the other is Caddy which operates the encrypted reverse proxy for SSL/TLS
# cd $AIMOA/ocr-container
# cd $OCRAPI/api
# docker compose up -d
#
# docker compose -f $AIMOA/ocr-container/docker-compose.yml up -d
docker compose -f $OCRAPI/api/docker-compose.yml up -d

# Check LLM and Caddy docker containers running
/bin/sleep 3
docker ps -a

# Returning to previous path location
cd $CURRENT
