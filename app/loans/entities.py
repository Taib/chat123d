import datetime
from typing import Literal
from app.db.guid import guid_gen
from app.db.sql.base_entity import (
    BaseEntity,
    type_created_at,
    type_updated_at,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String


class LoanEntity(BaseEntity):
    __tablename__ = "loans"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=guid_gen(16))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), nullable=False)
    due: Mapped[datetime.datetime] = mapped_column(nullable=False)
    returned_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)
    status: Mapped[Literal["active", "returned", "lost", "late"]] = mapped_column(
        nullable=False, default="active"
    )

    user: Mapped["UserEntity"] = relationship(back_populates="loans", foreign_keys=[user_id])  # noqa: F821
    book: Mapped["BookEntity"] = relationship(back_populates="loans")  # noqa: F821

    created_at: Mapped[type_created_at]
    updated_at: Mapped[type_updated_at]
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return f"Loan(id={self.id!r}, name={self.user_id!r} book={self.book_id!r})"
