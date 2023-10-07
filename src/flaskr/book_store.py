import dataclasses
from urllib.parse import unquote

import flask
from flask import Blueprint

from src.data.book_store.book import Book
from src.data.book_store.chapter import Chapter
from src.data.exceptions import CheckedException
from src.module import book_store_data_loader
from src.utils.flask_utils import create_success_response

book_store_blueprint = Blueprint("book_store", __name__, url_prefix="/flask/book_store")


@book_store_blueprint.route("/get_books", methods=["GET"])
def get_books():
    limit = int(flask.request.args.get("limit", 100))
    offset = int(flask.request.args.get("offset", 0))
    return create_success_response(
        **dataclasses.asdict(
            book_store_data_loader.get_books(limit=limit, offset=offset)
        )
    )


@book_store_blueprint.route("/get_catalogue", methods=["GET"])
def get_catalogue():
    limit = int(flask.request.args.get("limit", 65536))
    offset = int(flask.request.args.get("offset", 0))
    book_source = unquote(flask.request.args["book_source"] or "")
    book_identifier = unquote(flask.request.args["book_identifier"] or "")
    return create_success_response(
        **dataclasses.asdict(
            book_store_data_loader.get_catalogue(
                book_source=book_source,
                book_identifier=book_identifier,
                limit=limit,
                offset=offset,
            )
        )
    )


@book_store_blueprint.route("/get_chapter", methods=["GET"])
def get_chapter():
    book_source = unquote(flask.request.args["book_source"] or "")
    book_identifier = unquote(flask.request.args["book_identifier"] or "")
    chapter_identifier = unquote(flask.request.args["chapter_identifier"] or "")
    return create_success_response(
        **dataclasses.asdict(
            book_store_data_loader.get_chapter(
                book_source=book_source,
                book_identifier=book_identifier,
                chapter_identifier=chapter_identifier,
            )
        )
    )


@book_store_blueprint.route("/delete_books", methods=["DELETE"])
def delete_books():
    book_source = flask.request.json["book_source"] or ""
    book_identifier = flask.request.json["book_identifier"] or ""
    book_store_data_loader.book_dao.delete_by_values(
        book_source=book_source,
        book_identifier=book_identifier,
    )
    book_store_data_loader.chapter_dao.delete_by_values(
        book_source=book_source,
        book_identifier=book_identifier,
    )
    return create_success_response()


@book_store_blueprint.route("/delete_chapters", methods=["DELETE"])
def delete_chapters():
    book_source = flask.request.json["book_source"] or ""
    book_identifier = flask.request.json["book_identifier"] or ""
    chapter_identifier = flask.request.json["chapter_identifier"] or ""
    book_store_data_loader.chapter_dao.delete_by_values(
        book_source=book_source,
        book_identifier=book_identifier,
        chapter_identifier=chapter_identifier,
    )
    return create_success_response()


@book_store_blueprint.route("/create_books", methods=["POST"])
def create_books():
    books = flask.request.json.get("books", [])
    if not books:
        raise CheckedException("books are required")
    book_store_data_loader.book_dao.insert_or_replace(
        [Book.loads(book) for book in books]
    )
    return create_success_response()


@book_store_blueprint.route("/create_chapters", methods=["POST"])
def create_chapters():
    chapters = flask.request.json.get("chapters", [])
    if not chapters:
        raise CheckedException("chapters are required")
    book_store_data_loader.chapter_dao.insert_or_replace(
        [Chapter.loads(chapter) for chapter in chapters]
    )
    return create_success_response()
