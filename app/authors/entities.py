from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.db.guid import guid_gen
from app.db.sql.base_entity import (
    BaseEntity,
    type_created_at,
    type_updated_at,
)


class AuthorEntity(BaseEntity):
    __tablename__ = "authors"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=guid_gen(16))
    name: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    bio: Mapped[str] = mapped_column(String(4096), nullable=True)

    books = relationship("BookEntity", back_populates="author")  # noqa: F821

    created_at: Mapped[type_created_at]
    updated_at: Mapped[type_updated_at]
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return f"Author(id={self.id!r}, name={self.name!r})"
