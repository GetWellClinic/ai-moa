import logging
from src.config import ConfigManager

def setup_logging(config_path='config/config.yaml'):
    try:
        config = ConfigManager(config_path)
        logging_config = config.get('logging', {})
        
        # Map string log levels to logging constants
        log_level = getattr(logging, logging_config.get('level', 'INFO').upper(), logging.INFO)
        
        handlers = []
        
        # File handler
        if logging_config.get('filename'):
            file_handler = logging.FileHandler(logging_config['filename'])
            handlers.append(file_handler)
        
        # Console handler
        if logging_config.get('console', False):
            console_handler = logging.StreamHandler()
            handlers.append(console_handler)
        
        # Basic configuration
        logging.basicConfig(
            level=log_level,
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=handlers
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Logging setup completed")
        return logger
    
    except Exception as e:
        print(f"Error setting up logging: {e}")
        # Set up a basic logger in case of failure
        return logging.getLogger(__name__)
