import dataclasses
import io
import json
import os
from typing import List, Optional, Union

import requests
from sqlite_dao_ext import SqliteDataObject


# pylint: disable=R0801
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


@dataclasses.dataclass
class Book:
    book_source: str
    book_identifier: str

    url: str
    title: str

    created_at: str = None
    updated_at: str = None

    count_chapters: int = None


@dataclasses.dataclass
class CatalogueItem:
    title: str
    chapter_identifier: str


@dataclasses.dataclass
class GetBooksResponse:
    books: List[Book]


@dataclasses.dataclass
class GetCatalogueResponse:
    book: Book
    catalogue_items: List[CatalogueItem]


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


# pylint: enable=R0801


class Client:
    url: str
    sess: requests.Session

    def __init__(self, url: str, sess: requests.Session = None):
        self.url = url
        self.sess = sess if sess else requests.Session()

    def home(self):
        return self.get("/").text

    def ftp_list_dir(self, dir_path: str):
        return self.get("/flask/ftp/list_dir", dir_path=dir_path).json()

    def ftp_create_folder(self, dir_path: str):
        return self.post("/flask/ftp/create_folder", dir_path=dir_path).json()

    def ftp_upload(
        self,
        file_path: str,
        override: bool = False,
        file_data: bytes = None,
        local_file_path: str = None,
    ):
        if file_data is not None:
            stream = io.BytesIO(file_data)
        elif local_file_path is not None:
            # pylint: disable=R1732
            stream = open(local_file_path, "rb")
            # pylint: enable=R1732
        else:
            raise RuntimeError("file_data and local_file_path are both none")
        return self.sess.post(
            self._build_url_path("/flask/ftp/upload"),
            data={"file_path": file_path, "override": override},
            files=[("file", (os.path.basename(file_path), stream, "text/plain"))],
        ).json()

    def ftp_download(self, file_path: str, password: Optional[str] = None):
        return self.get("/flask/ftp/download", file_path=file_path, password=password)

    def ftp_delete(self, path: str):
        return self.delete("/flask/ftp/delete", path=path).json()

    def item_get(
        self,
        source: str,
        cipher_identifier: Optional[str] = None,
        name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> List[UnifiedItem]:
        return [
            UnifiedItem.loads(item)
            for item in self.get(
                "/flask/item/get",
                source=source,
                cipher_identifier=cipher_identifier,
                name=name,
                password=password,
            ).json()["items"]
        ]

    def item_insert(self, items: List[UnifiedItem]):
        return self.post(
            "/flask/item/insert", items=[item.dumps() for item in items]
        ).json()

    def item_delete(
        self, source: str, cipher_identifier: str, name: Optional[str] = None
    ):
        return self.delete(
            "/flask/item/delete",
            source=source,
            cipher_identifier=cipher_identifier,
            name=name,
        ).json()

    def book_store_create_books(self, books: List[Book]):
        return self.post(
            "/flask/book_store/create_books",
            books=[dataclasses.asdict(book) for book in books],
        ).json()

    def book_store_create_chapters(self, chapters: List[Chapter]):
        return self.post(
            "/flask/book_store/create_chapters",
            chapters=[chapter.dumps() for chapter in chapters],
        ).json()

    def book_store_delete_books(self, book_source: str, book_identifier: str):
        return self.delete(
            "/flask/book_store/delete_books",
            book_source=book_source,
            book_identifier=book_identifier,
        ).json()

    def book_store_delete_chapters(
        self, book_source: str, book_identifier: str, chapter_identifier: str
    ):
        return self.delete(
            "/flask/book_store/delete_chapters",
            book_source=book_source,
            book_identifier=book_identifier,
            chapter_identifier=chapter_identifier,
        ).json()

    def book_store_get_books(self, limit: int = 100, offset: int = 0) -> List[Book]:
        return [
            Book(**book)
            for book in self.get(
                "/flask/book_store/get_books", limit=limit, offset=offset
            ).json()["response"]["books"]
        ]

    def book_store_get_catalogue(
        self,
        book_source: str,
        book_identifier: str,
        limit: int = 65536,
        offset: int = 0,
    ) -> GetCatalogueResponse:
        return GetCatalogueResponse(
            **self.get(
                "/flask/book_store/get_catalogue",
                book_source=book_source,
                book_identifier=book_identifier,
                limit=limit,
                offset=offset,
            ).json()["response"]
        )

    def book_store_get_chapter(
        self, book_source: str, book_identifier: str, chapter_identifier: str
    ) -> Chapter:
        return Chapter.loads(
            self.get(
                "/flask/book_store/get_chapter",
                book_source=book_source,
                book_identifier=book_identifier,
                chapter_identifier=chapter_identifier,
            ).json()["chapter"]
        )

    def get(self, url_path: str, **params):
        return self.sess.get(self._build_url_path(url_path), params=params)

    def post(self, url_path: str, **data):
        return self.sess.post(self._build_url_path(url_path), json=data)

    def delete(self, url_path: str, **data):
        return self.sess.delete(self._build_url_path(url_path), json=data)

    def _build_url_path(self, url_path: str):
        return self.url.rstrip("/") + "/" + url_path.lstrip("/")
