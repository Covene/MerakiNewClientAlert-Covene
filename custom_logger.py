import logging
from logging.handlers import RotatingFileHandler
import os

loggers = {}

def setup_logger(name, log_file, level=logging.INFO, console=True):  # Set console=True by default
    """
    :param name: Logger name
    :param log_file: File to log messages to
    :param level: Logging level
    :param console: Boolean to indicate if logs should also be printed to console
    :return: Configured logger
    """
    global loggers

    if loggers.get(name):
        return loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a rotating file handler
    try:
        handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    except IOError as e:
        logger.error(f"Failed to open log file {log_file}: {e}")
        return None
    
    handler.setLevel(level)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Always add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    loggers[name] = logger
    return logger