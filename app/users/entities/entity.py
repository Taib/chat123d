from typing import Literal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, Integer, String

from app.db.guid import guid_gen
from app.db.sql.base_entity import BaseEntity, type_created_at, type_updated_at


class UserEntity(BaseEntity):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=guid_gen(16))
    role: Mapped[Literal["loaner", "librarian", "admin"]] = mapped_column(
        default="loaner"
    )
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(4096), nullable=False)
    address: Mapped[str] = mapped_column(String(1024), nullable=False)

    max_week_loans: Mapped[int] = mapped_column(
        Integer, nullable=True, default=lambda: 3
    )

    loan_preferences: Mapped[str] = mapped_column(JSON, nullable=True) # favorite genres, etc.

    loans: Mapped[list["LoanEntity"]] = relationship(  # noqa: F821
        back_populates="user", foreign_keys="[LoanEntity.user_id]"
    )

    # banned_until: Mapped[datetime.datetime] = mapped_column(nullable=True)
    created_at: Mapped[type_created_at]
    updated_at: Mapped[type_updated_at]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r} address={self.address!r} max_week_loans={self.max_week_loans!r}, role={self.role!r})"
