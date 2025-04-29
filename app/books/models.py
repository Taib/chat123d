import datetime
from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author_id: str
    year: int
    publisher: str | None = None
    isbn: str | None = None
    cover_image: str | None = None
    status: str = "available"
    note: float | None = None
    short_description: str | None = None
    description: str | None = None


class BookUpdate(BaseModel):
    id: str
    title: str | None = None
    author_id: str | None = None
    year: int | None = None
    publisher: str | None = None
    isbn: str | None = None
    cover_image: str | None = None
    status: str | None = None
    note: float | None = None
    short_description: str | None = None
    description: str | None = None


class Book(BaseModel):
    id: str
    title: str
    author_id: str
    author: dict | None = None
    year: int
    publisher: str | None = None
    isbn: str | None = None
    cover_image: str | None = None
    status: str = "available"
    note: float | None = None
    short_description: str | None = None
    description: str | None = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None
