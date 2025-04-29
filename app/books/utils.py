from typing import Literal

from sqlalchemy import text

from app.db.sql.base_engine import base_session
from app.books.models import Book
from app.books.utils_book_note import fetch_goodreads_rating_by_isbn

import logging
logger = logging.getLogger("liboo.app.books.utils")


def order_books(
    books: list[Book],
    order_by: Literal["pertinance", "year"] = "year",
) -> list[Book]:
    """
    Order books by pertinance or year.
    """
    match order_by:
        case "pertinance":
            # TODO: something based on user's preference
            return sorted(books, key=lambda x: x.year, reverse=True)
        case "year":
            return sorted(books, key=lambda x: x.year, reverse=True)
        case _:
            raise ValueError("Invalid order_by value")


def update_book_note_if_isbn_found(
    *,
    isbn: str,
    book_id: str
):
    try:
        note = fetch_goodreads_rating_by_isbn(isbn)
        if note is None:
            return
        with base_session() as session:
            session.execute(
                text("UPDATE books SET note = :note WHERE id = :id"),
                {"id": book_id, "note": note},
            )
            session.commit()
    except Exception as e:
        logger.error(f"Error updating book note: {e}")
