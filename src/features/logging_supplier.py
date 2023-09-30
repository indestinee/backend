import logging

from src.config import LoggingConfig


def get_logger(name: str = "werkzeug") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LoggingConfig.logging_level)
    formatter = logging.Formatter("[%(levelname)s][%(name)s][%(asctime)s] %(message)s")

    if LoggingConfig.logging_file:
        file_handler = logging.FileHandler(LoggingConfig.logging_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(LoggingConfig.logging_level)
    steam_handler.setFormatter(formatter)
    logger.addHandler(steam_handler)
    return logger
