import logging
from logging.handlers import RotatingFileHandler
from config.config_manager import ConfigManager

def setup_logging(config: ConfigManager):
    """
    Set up logging for the application, including both file and console handlers.
    
    This function configures a root logger to output logs to both the console 
    and a rotating log file. The log level and format are determined by the 
    provided configuration.

    If both the `RotatingFileHandler` and `StreamHandler` are already set 
    for the root logger, the function will not modify the existing logging 
    configuration and will simply return the existing logger.

    Args:
        config (ConfigManager): A configuration manager instance that provides
                                the logging configuration.

    Returns:
        logging.Logger: The configured root logger with the appropriate handlers.
    
    Configuration options:
        - 'logging.format': A string defining the log message format. Defaults to 
          '%(asctime)s - %(name)s - %(levelname)s - %(message)s'.
        - 'logging.filename': The log file name. Defaults to 'workflow.log'.
        - 'logging.file_level': The log level for file handler. Defaults to 'DEBUG'.
        - 'logging.console_level': The log level for console handler. Defaults to 'INFO'.

    Example:
        config = ConfigManager()
        logger = setup_logging(config)
        logger.debug("This is a debug message.")
    """
    logging_config = config.get('logging', {})
    
    # Set up root logger
    root_logger = logging.getLogger()


    # Check if the specific handlers already exist
    file_handler_exists = any(isinstance(handler, RotatingFileHandler) for handler in root_logger.handlers)
    console_handler_exists = any(isinstance(handler, logging.StreamHandler) for handler in root_logger.handlers)

    # If both handlers exist, return the logger without modifying it
    if file_handler_exists and console_handler_exists:
        return root_logger

    root_logger.setLevel(logging.DEBUG)  # Capture all levels, filter at handlers

    # Create formatters
    formatter = logging.Formatter(logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # File Handler
    file_handler = RotatingFileHandler(
        logging_config.get('filename', 'workflow.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.getLevelName(logging_config.get('file_level', 'DEBUG')))
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.getLevelName(logging_config.get('console_level', 'INFO')))
    console_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger
