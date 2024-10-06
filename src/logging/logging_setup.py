import logging
from src.config.config_manager import ConfigManager

def setup_logging(config: ConfigManager):
    logging_config = config.get('general.logging', {})
    logging.config.dictConfig(logging_config)
    return logging.getLogger(__name__)
