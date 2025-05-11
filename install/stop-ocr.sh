#!/bin/bash
# Shutdown script for local OCR Docker Containers
# Version 2025.05.10

# CONFIGURATION:
# Automatic detection of base directory for AI-MOA:
cd ..
AIMOA=$(pwd)
# Override by specifying full path to AI-MOA base directory:
# AIMOA=/opt/ai-moa
OCRAPI=/opt/doctr

# Confirm base directory for AI-MOA:
/bin/echo "Specifying AI-MOA base directory..."
/bin/echo $AIMOA

# Run AI LLM Containers:
# Note: Two containers will stop, one for OCR container, the other is Caddy which operates the encrypted reverse proxy for SSL/TLS
# cd $OCRAPI
# docker compose down -d
#
/bin/echo "Halting OCR Containers..."
docker compose -f $OCRAPI/api/docker-compose.yml down

# Check LLM and Caddy docker containers running
/bin/sleep 3
docker ps -a
