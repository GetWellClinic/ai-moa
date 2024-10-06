import logging
from logging.handlers import RotatingFileHandler
from src.config.config_manager import ConfigManager

def setup_logging(config: ConfigManager):
    logging_config = config.get('logging', {})
    
    # Set up root logger
    root_logger = logging.getLogger()
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
