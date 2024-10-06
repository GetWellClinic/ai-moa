import logging
from src.config import ConfigManager

def setup_logging():
    config = ConfigManager('config/config.yaml')
    logging_config = config.get('logging', {})
    
    logging.basicConfig(
        level=logging_config.get('level', 'INFO'),
        format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        filename=logging_config.get('filename')
    )
    
    return logging.getLogger(__name__)
