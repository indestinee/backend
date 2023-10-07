import dataclasses
import json
from typing import List, Union

from sqlite_dao_ext import SqliteDataObject


@dataclasses.dataclass
class Media:
    text: str = None
    image_url: str = None
    image_base64: str = None  # base64


@dataclasses.dataclass(init=False)
class Chapter(SqliteDataObject):
    book_source: str
    book_identifier: str

    chapter_identifier: str

    url: str
    title: str
    content: List[Media]

    @classmethod
    def primary_keys(cls) -> List[str]:
        return ["book_source", "book_identifier", "chapter_identifier"]

    @classmethod
    def _load__content(cls, value: Union[str, list]) -> List[Media]:
        if isinstance(value, str):
            value = json.loads(value)
        return [Media(**media) for media in value]

    @classmethod
    def _dump__content(cls, medias: List[Media]) -> str:
        return json.dumps([dataclasses.asdict(media) for media in medias])
