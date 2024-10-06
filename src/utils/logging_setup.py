import logging

def setup_logging(config):
    logging.basicConfig(
        level=config.get('logging', {}).get('root', {}).get('level', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
