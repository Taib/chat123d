from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks

from app.auth.auth_guard import (
    get_librarian_active_user,
    get_current_active_user,
    get_user_from_token,
)
from app.books.repository import BookRepository
from app.books.models import BookCreate, BookUpdate
from app.books.utils import update_book_note_if_isbn_found


import logging

logger = logging.getLogger("liboo.app.books.controller")

books_router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@books_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
)
async def query_books(
    query: str = Query(None, min_length=3),
    order_by: Literal["pertinance", "year"] = Query("year"),
    repo: BookRepository = Depends(),
):
    """
    Query books with filters.
    """
    try:
        return repo.query_books(q=query, order_by=order_by)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@books_router.get(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_librarian_active_user)],
)
async def get_book(
    book_id: str,
    repo: BookRepository = Depends(),
):
    """
    Get a book by ID.
    """
    try:
        book = repo.get_book(book_id)
        if not book:
            raise ValueError("Book not found")
        return book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@books_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_librarian_active_user)],
)
async def create_book(
    *,
    book: BookCreate,
    repo: BookRepository = Depends(),
    user_token: str = Depends(get_user_from_token),
    background_tasks: BackgroundTasks,
):
    """
    Create a new book.
    """
    try:
        result = repo.create_book(book)
        if result and result.isbn:
            background_tasks.add_task(
                update_book_note_if_isbn_found,
                isbn=result.isbn,
                book_id = result.id
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@books_router.put(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_librarian_active_user)],
)
async def update_book(
    book: BookUpdate,
    repo: BookRepository = Depends(),
):
    """
    Update a book.
    """
    try:
        return repo.update_book(book)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@books_router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_librarian_active_user)],
)
async def delete_book(
    book_id: str,
    repo: BookRepository = Depends(),
):
    """
    Delete a book.
    """
    try:
        logger.debug(f"delete_book: {book_id=}")
        result = repo.delete_book(book_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
