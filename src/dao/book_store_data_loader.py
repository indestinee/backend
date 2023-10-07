from typing import Dict, Any, Union

from sqlite_dao_ext import SqliteDao, SqliteClient
from src.data.book_store import book_store_service
from src.data.book_store.book import Book
from src.data.book_store.book_store_service import (
    GetBooksResponse,
    GetCatalogueResponse,
    CatalogueItem,
)
from src.data.book_store.chapter import Chapter
from src.data.exceptions import CheckedException


class BookStoreDataLoader:
    sqlite_client: SqliteClient
    book_dao: SqliteDao[Book]
    chapter_dao: SqliteDao[Chapter]

    CONNECTOR = "!@#FJSKAH#*@!DAS"

    def __init__(self, sqlite_client: SqliteClient):
        self.sqlite_client = sqlite_client
        self.book_dao = SqliteDao[Book](sqlite_client, Book)
        self.chapter_dao = SqliteDao[Chapter](sqlite_client, Chapter)

    def get_books(self, offset: int = 0, limit: int = 100) -> GetBooksResponse:
        books = self.book_dao.query_by_values(limit, offset)
        count_list = self.chapter_dao.count_group_by_values(
            group_by=["book_source", "book_identifier"]
        )
        count_map = {self._join_key(item): item["count"] for item in count_list}

        return GetBooksResponse(
            [
                book_store_service.Book.of(book, count_map.get(self._join_key(book), 0))
                for book in books
            ]
        )

    def get_catalogue(
        self,
        book_source: str,
        book_identifier: str,
        offset: int = 0,
        limit: int = 65536,
    ) -> GetCatalogueResponse:
        books = self.book_dao.query_by_values(
            book_source=book_source, book_identifier=book_identifier
        )

        if len(books) != 1:
            raise CheckedException("no such book")

        count = self.chapter_dao.count_by_values(
            book_source=book_source, book_identifier=book_identifier
        )
        catalogue_items = [
            CatalogueItem(**catalogue_item)
            for catalogue_item in self.chapter_dao.query_fields_by_values(
                fields=["title", "chapter_identifier"], offset=offset, limit=limit
            )
        ]

        return GetCatalogueResponse(
            book=book_store_service.Book.of(books[0], count),
            catalogue_items=catalogue_items,
        )

    def get_chapter(
        self, book_source: str, book_identifier: str, chapter_identifier: str
    ) -> Chapter:
        chapters = self.chapter_dao.query_by_values(
            book_source=book_source,
            book_identifier=book_identifier,
            chapter_identifier=chapter_identifier,
        )

        if len(chapters) != 1:
            raise CheckedException("no such book")

        chapter = chapters[0]
        return chapter

    def _join_key(self, book: Union[Dict[str, Any], Book]):
        return self.CONNECTOR.join([book["book_source"], book["book_identifier"]])
