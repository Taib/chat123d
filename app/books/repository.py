from typing import Literal
from fastapi import Depends
from app.books.entities import BookEntity
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, or_
from app.db.sql.base_repository import BaseRepository
from app.db.sql.utils import pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from app.books.models import Book, BookCreate, BookUpdate
from app.db.get_db import get_db
from app.books.utils import order_books
from app.auth.auth_guard import get_current_active_user
from app.users.models.models import User

import logging

logger = logging.getLogger("liboo.app.books.repository")


def book_entity_to_model(entity: BookEntity) -> Book:
    """
    Convert a BookEntity to a model.
    """
    return sqlalchemy_to_pydantic(entity, Book, exclude={"password"})


def book_model_to_entity(model: Book) -> BookEntity:
    """
    Convert a model to a BookEntity.
    """
    return pydantic_to_sqlalchemy(model, BookEntity, exclude_unset=True)


class BookRepository(BaseRepository[BookEntity]):
    def __init__(
        self,
        session: Session = Depends(get_db),
        user: User = Depends(get_current_active_user),
    ):
        super().__init__(BookEntity, session)
        self.user = user

    def get_book(self, book_id: str) -> Book | None:
        """
        Get a book by ID.
        """
        book = self.find_by_id(book_id)
        if book:
            return book_entity_to_model(book)
        return None

    def query_books(
        self, *, q: str | None, order_by: Literal["pertinance", "year"] = "year"
    ) -> list[Book]:
        """
        Query books with filters.
        """
        logger.debug(f"query_books: {q=}, {order_by=}")
        if not q:
            stmt = select(BookEntity).options(
                joinedload(BookEntity.author),
            )
            logger.debug(f"query_books: {stmt=}")
            result = self.session.execute(stmt)
            logger.debug(f"query_result: {result=}")
            books = result.scalars().all()
        else:
            search_pattern = f"%{q}%"
            books = (
                self.query()
                .filter(
                    or_(
                        BookEntity.title.ilike(search_pattern),
                        BookEntity.description.ilike(search_pattern),
                        BookEntity.isbn.ilike(search_pattern),
                    )
                )
                .all()
            )

        return order_books([book_entity_to_model(book) for book in books], order_by)

    def get_book_by_name(self, name: str) -> Book | None:
        """
        Get a book by name.
        """
        book = self.query().filter_by(name=name).first()
        if book:
            return book_entity_to_model(book)
        return None

    def create_book(self, book: BookCreate) -> Book:
        """
        Create a new book.
        """

        try:
            entity = book_model_to_entity(book)
            entity.created_by = self.user.id
            entity.updated_by = self.user.id
            result = self.create(entity)
            return book_entity_to_model(result)
        except Exception as e:
            print(f"Error creating book: {e}")
            logger.error(f"Error creating book {e}")
            raise ValueError("book-creation-failed")

    def update_book(self, book: BookUpdate) -> Book:
        """
        Update an existing book.
        """
        dump = book.model_dump(exclude_unset=True)
        dump["updated_by"] = self.user.id
        self.update(book.id, dump)
        return self.find_by_id(book.id)

    def delete_book(self, book_id: str) -> bool:
        """
        Delete a book by ID.
        """
        return self.delete(book_id)
