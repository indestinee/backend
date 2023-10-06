import json
import logging
import os
import re
from io import BytesIO
from typing import Tuple, List, Dict

from src.config import FtpConfig
from src.data.cipher import Cipher
from src.data.file_system_object import FileSystemObject
from src.features.cipher_supplier import CipherSupplier
from src.features.exceptions import CheckedException
from src.features.logging_supplier import get_logger


class FtpSupplier:
    cipher_supplier: CipherSupplier
    _logger: logging.Logger = get_logger("ftp")
    _invalid_path_pattern = re.compile(r"(^|/)\.\.(/|$)")

    def __init__(self, cipher_supplier: CipherSupplier):
        self.cipher_supplier = cipher_supplier
        if not os.path.exists(FtpConfig.ftp_root_path):
            os.makedirs(FtpConfig.ftp_root_path)
        assert os.path.isdir(FtpConfig.ftp_root_path)

    def list_dir(self, dir_path: str) -> List[FileSystemObject]:
        dir_path, abs_path = self.get_abs_path(dir_path, check_is_dir=True)
        fps = [os.path.join(dir_path, file_name) for file_name in os.listdir(abs_path)]
        return list(map(self.file_stat, fps))

    def file_stat(self, file_path: str) -> FileSystemObject:
        _, abs_path = self.get_abs_path(file_path, check_exists=True)
        return FileSystemObject.from_stat(file_path, abs_path, os.stat(abs_path))

    def get_abs_path(
        self,
        path: str,
        *,
        check_is_dir=False,
        check_is_file=False,
        check_exists=False,
        check_not_exists=False,
    ) -> Tuple[str, str]:
        path = os.path.normpath(path)
        abs_path = os.path.abspath(os.path.join(FtpConfig.ftp_root_path, path))
        if path.startswith("/") or self._invalid_path_pattern.search(path):
            raise CheckedException(f"invalid path: {path}")
        if not abs_path.startswith(FtpConfig.ftp_root_path):
            raise CheckedException(f"invalid path: {path}")
        if check_is_file and not os.path.isfile(abs_path):
            raise CheckedException(f"target is not a file: {path}")
        if check_is_dir and not os.path.isdir(abs_path):
            raise CheckedException(f"target is not a dir: {path}")
        if check_exists and not os.path.exists(abs_path):
            raise CheckedException(f"file does not exist: {path}")
        if check_not_exists and os.path.exists(abs_path):
            raise CheckedException(f"file exists: {path}")
        return path, abs_path

    def decrypt_file(self, file_path: str, password: str) -> Dict:
        file_path, abs_path = self.get_abs_path(file_path, check_is_file=True)
        try:
            with open(abs_path, "rb") as file_stream:
                cipher = Cipher(**json.load(file_stream))
            decrypted_data = json.loads(
                self.cipher_supplier.decrypt(password, cipher.dumps())
            )
            is_hex = decrypted_data.pop("is_hex", False)
            file_data = decrypted_data.pop("file_data", "")
            byte_io = BytesIO()
            byte_io.write(
                bytes.fromhex(file_data) if is_hex else file_data.encode("utf-8")
            )
            byte_io.seek(0)
            return {
                "file_data": byte_io,
                **decrypted_data,
            }

        except Exception as exception:
            self._logger.debug("decrypt file failed with %s", exception)
            raise CheckedException("decryption failure")
