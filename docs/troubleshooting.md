# AI-MOA Troubleshooting Guide

This guide addresses common issues that you might encounter while working with AI-MOA and provides solutions to resolve them.

## How to start AI-MOA running

Once you have installed, and configured AI-MOA, you can start AI-MOA by executing the following command:
```
cd src
python3 main.py --run-immediately
```

If you get run errors, be sure to check read-write permissions are set for your user for
../config directory and the config files in ../config/*
as AI-MOA will need to save/write "provider_list.yaml" to the config directory and also needs to be able to write to "config.yaml" file.

You can also specify the location of config files by passing on some parameters, when executing start command:
```
python3 main.py --config ../config/config.yaml --workflow-config ../config/workflow-config.yaml --cron-interval */5 --run-immediately
```

## Login Issues

### Problem: Unable to log in to the O19 EMR system

1. Check your credentials in the `config.yaml` file.
2. Ensure the O19 EMR system is accessible and running.
3. Verify that you have the correct permissions to access the system.

## Document Processing Issues

### Problem: OCR is not working correctly

1. Check if doctr OCR is installed and properly configured.
2. Verify the `ocr` settings in the configuration file.
3. Ensure the PDF files are not corrupted or password-protected.

### Problem: AI model is not responding

1. Check the AI API configuration in `config.yaml`.
2. Verify that the AI service is running and accessible.
3. Check the API logs for any error messages.

## Workflow Execution Issues

### Problem: Workflow steps are not executing in the expected order

1. Review the workflow configuration in `workflow-config.yaml`.
2. Check the logs for any error messages during workflow execution.
3. Verify that all required functions for each step are implemented.

## Performance Issues

### Problem: System is running slowly

1. Check the system resources (CPU, memory, disk space).
2. Review the logging level and reduce if necessary.
3. Consider optimizing database queries or increasing hardware resources.

## Docker-related Issues

### Problem: Docker container fails to start

1. Check Docker logs for error messages.
2. Verify that all required environment variables are set.
3. Ensure that the necessary ports are available and not in use by other services.

## Task Persistence Issues

### Problem: Tasks are lost when the application restarts

This is expected behavior with the current in-memory Huey configuration. If task persistence across restarts is required, consider configuring Huey with Redis or SQLite backend.

## Debugging Tips

1. Enable debug logging by setting the log level to DEBUG in `config.yaml`.
2. Check if the lock status in `config.yaml` is set to true. If it is true, the system will skip file processing. Change it to false only if you are sure that all other processes have stopped.
3. Check the application logs for detailed error messages and stack traces.
4. If the application is stuck processing a file, check if the processors are overlapping (e.g., the config file's last processed file update and fetch).
5. Check if the application is using the GPU if there is excessive waiting time. OCR and LLM should be using the GPU by default.
6. Check O19 server logs if documents are not being updated (check app logs for more details).

If you encounter any issues not covered in this guide, please open an issue on the GitHub repository with a detailed description of the problem and steps to reproduce it.
