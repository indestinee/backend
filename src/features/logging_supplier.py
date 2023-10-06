import logging

from src.config import ServerConfig


def get_logger(name: str = "werkzeug") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(ServerConfig.logging_level)
    formatter = logging.Formatter("[%(levelname)s][%(name)s]: %(message)s")

    if ServerConfig.logging_file:
        file_handler = logging.FileHandler(ServerConfig.logging_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(ServerConfig.logging_level)
    steam_handler.setFormatter(formatter)
    logger.addHandler(steam_handler)
    return logger
