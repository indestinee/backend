import logging
import os
from argparse import ArgumentParser


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--db", default=None, help="database path", required=True)
    return parser.parse_args()


class ServerConfig:
    db_path = os.path.abspath("/tmp/mountd/disk1_part1/backend/backend.db")
    # db_path = os.path.abspath("/tmp/backend.db")
    ftp_root_path = os.path.abspath("/tmp/mountd/disk1_part1/Files")
    # root_path = os.path.abspath("/tmp/ftp")

    # logging
    logging_level = logging.WARNING
    logging_file = None


get_args()


class CipherConfig:
    hash_method: str = "sha256"
    cipher_size: int = 256
    salt_size: int = 256
