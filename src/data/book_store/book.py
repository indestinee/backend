import dataclasses
from typing import List
from sqlite_dao_ext import SqliteDataObject


@dataclasses.dataclass(init=False)
class Book(SqliteDataObject):
    book_source: str
    book_identifier: str

    url: str
    title: str

    @classmethod
    def primary_keys(cls) -> List[str]:
        return ["book_source", "book_identifier"]
