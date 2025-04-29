from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from app.db.guid import guid_gen
from app.db.sql.base_entity import (
    BaseEntity,
    type_created_at,
    type_updated_at,
)
from app.authors.entities import AuthorEntity


class BookEntity(BaseEntity):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=guid_gen(16))
    title: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    note: Mapped[float] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="available")
    author_id = mapped_column(ForeignKey("authors.id"), nullable=False)

    year: Mapped[int] = mapped_column(nullable=False)

    tags: Mapped[str] = mapped_column(String(1024), nullable=True)

    description: Mapped[str] = mapped_column(String(4096), nullable=True)
    short_description: Mapped[str] = mapped_column(String(512), nullable=True)

    cover_image: Mapped[str] = mapped_column(String(4096), nullable=True)
    publisher: Mapped[str] = mapped_column(String(256), nullable=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=True)

    author: Mapped["AuthorEntity"] = relationship(back_populates="books")
    loans: Mapped[list["LoanEntity"]] = relationship(  # noqa: F821
        back_populates="book",
        cascade="all,delete",
    )
    created_at: Mapped[type_created_at]
    updated_at: Mapped[type_updated_at]
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, name={self.title!r}, author={self.author!r})"
