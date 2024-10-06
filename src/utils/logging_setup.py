import logging


def setup_logging(config):
    """Set up logging configuration based on the provided config."""
    logging.basicConfig(
        level=config.get('logging', {}).get('root', {}).get('level', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
