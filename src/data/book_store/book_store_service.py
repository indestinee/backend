import dataclasses

from typing import List

from src.data.book_store.book import Book as BookDb
from src.utils.mics_utils import format_time


@dataclasses.dataclass
class Book:
    book_source: str
    book_identifier: str

    url: str
    title: str

    created_at: str
    updated_at: str

    count_chapters: int

    @classmethod
    def of(cls, book: BookDb, count: int) -> "Book":
        return Book(
            book_source=book.book_source,
            book_identifier=book.book_identifier,
            url=book.url,
            title=book.title,
            created_at=format_time(book.created_at),
            updated_at=format_time(book.updated_at),
            count_chapters=count,
        )


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
