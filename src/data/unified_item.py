import dataclasses
from typing import List

from sqlite_dao_ext import SqliteDataObject


@dataclasses.dataclass(init=False)
class UnifiedItem(SqliteDataObject):
    source: str
    cipher_identifier: str
    name: str

    data: str
    is_encrypted: bool
    note: str = None

    @classmethod
    def primary_keys(cls) -> List[str]:
        return ["source", "cipher_identifier", "name"]
