
import logging
import logging.config
import pathlib

BASE_DIR = pathlib.Path(__file__).parent


def setup_logger(app, log_config_path=None):
    if log_config_path is None:
        log_config_path = BASE_DIR / 'config' / 'logging.conf'

    logging.config.fileConfig(log_config_path)
    logger = logging.getLogger(app['config']['app']['name'])

    app.logger = logger
