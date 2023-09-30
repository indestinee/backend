import logging
import os.path


class DatabaseConfig:
    db_path = os.path.abspath("/tmp/mountd/disk1_part1/backend/backend.db")
    # db_path = os.path.abspath("/tmp/backend.db")


class FtpConfig:
    root_path = os.path.abspath("/tmp/mountd/disk1_part1/Files")
    # root_path = os.path.abspath("/tmp/ftp")


class LoggingConfig:
    logging_level = logging.WARNING
    logging_file = None


class CipherConfig:
    hash_method: str = "sha256"
    cipher_size: int = 256
    salt_size: int = 256
