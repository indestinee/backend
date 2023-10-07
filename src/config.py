import logging
import os


class ServerConfig:
    db_path = os.environ.get("DB_PATH", ":memory:")
    ftp_root_path = os.path.abspath(os.environ.get("FTP_ROOT_PATH", "/tmp/ftp"))

    # logging
    logging_level = logging.WARNING
    logging_file = None


class CipherConfig:
    hash_method: str = "sha256"
    cipher_size: int = 256
    salt_size: int = 256
