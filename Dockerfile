FROM python:3.9

WORKDIR /app

# Copy the source code
COPY src /app/src

# Copy the configuration files
COPY src/config/*.yaml /app/src/config/
COPY src/config.yaml /app/src/config.yaml
COPY src/workflow-config.yaml /app/src/workflow-config.yaml

# Install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory to src
WORKDIR /app/src

# Run the application
CMD ["python", "main.py"]
