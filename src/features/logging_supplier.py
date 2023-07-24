import logging

from src.config import LoggingConfig


def get_logger(
    name: str = "werkzeug", logging_level: int = LoggingConfig.logging_level
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    fh = logging.FileHandler("/tmp/backend.log")
    ch = logging.StreamHandler()
    ch.setLevel(logging_level)
    formatter = logging.Formatter("[%(levelname)s][%(name)s][%(asctime)s] %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
