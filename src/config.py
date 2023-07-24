import logging
import os.path


class DatabaseConfig:
    db_path = os.path.abspath("/tmp/backend.db")


class FtpConfig:
    root_path = os.path.abspath("/tmp/ftp")


class LoggingConfig:
    logging_level = logging.DEBUG
