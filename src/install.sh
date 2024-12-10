#!/bin/bash

# Create the logs directory if it doesn't exist
mkdir -p ../logs

# Create the static directory if it doesn't exist
mkdir -p static

# Install Python dependencies from requirements.txt
pip install -r requirements.txt
