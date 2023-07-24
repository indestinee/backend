import logging
import os
import re
from typing import List

from src.config.ftp_config import FtpConfig
from src.data.file_system_object import FileSystemObject
from src.features.exceptions import CheckedException
from src.features.logging_supplier import get_logger


class FtpSupplier:
    logger: logging.Logger = get_logger("ftp")
    invalid_path_pattern = re.compile(r"(^|/)\.\.(/|$)")

    def __init__(self):
        if not os.path.exists(FtpConfig.root_path):
            os.makedirs(FtpConfig.root_path)
        assert os.path.isdir(FtpConfig.root_path)

    def list_dir(self, dir_path: str) -> List[FileSystemObject]:
        dir_path, abs_path = self.get_abs_path(dir_path, check_is_dir=True)
        fps = [os.path.join(dir_path, file_name) for file_name in os.listdir(abs_path)]
        return list(map(self.file_stat, fps))

    def file_stat(self, file_path: str) -> FileSystemObject:
        dir_path, abs_path = self.get_abs_path(file_path, check_exists=True)
        return FileSystemObject.from_stat(file_path, abs_path, os.stat(abs_path))

    def get_abs_path(
        self,
        path: str,
        *,
        check_is_dir=False,
        check_is_file=False,
        check_exists=False,
        check_not_exists=False,
    ) -> tuple[str, str]:
        path = os.path.normpath(path)
        abs_path = os.path.abspath(os.path.join(FtpConfig.root_path, path))
        if path.startswith("/") or self.invalid_path_pattern.search(path):
            raise CheckedException(f"invalid path: {path}")
        if not abs_path.startswith(FtpConfig.root_path):
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
