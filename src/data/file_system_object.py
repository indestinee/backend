import dataclasses
import os
from enum import Enum


class FileType(str, Enum):
    file = "file"
    dir = "dir"


@dataclasses.dataclass
class FileSystemObject:
    name: str
    path: str
    type: FileType = None
    size: int = None
    created_at: float = None
    updated_at: float = None

    @classmethod
    def from_stat(cls, file_path, abs_path, stat: os.stat_result):
        return FileSystemObject(
            os.path.basename(file_path),
            os.path.dirname(file_path),
            type=FileType.dir if os.path.isdir(abs_path) else FileType.file,
            size=stat.st_size if os.path.isfile(abs_path) else 0,
            created_at=stat.st_ctime,
            updated_at=stat.st_mtime,
        )
