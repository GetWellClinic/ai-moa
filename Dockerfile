FROM python:3.9

WORKDIR /app

# Copy the source code
COPY src /app/src

# Copy the configuration files
COPY src/config.yaml /app/src/config.yaml
COPY src/workflow-config.yaml /app/src/workflow-config.yaml

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Uvicorn
RUN pip install uvicorn

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
