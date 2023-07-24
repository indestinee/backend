import logging

from src.config import LoggingConfig


def get_logger(
    name: str = "werkzeug", logging_level: int = LoggingConfig.logging_level
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    file_handler = logging.FileHandler("/tmp/backend.log")
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging_level)
    formatter = logging.Formatter("[%(levelname)s][%(name)s][%(asctime)s] %(message)s")
    file_handler.setFormatter(formatter)
    steam_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(steam_handler)
    return logger
