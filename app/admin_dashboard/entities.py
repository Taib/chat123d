from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON
from app.db.guid import guid_gen
from sqlalchemy import UniqueConstraint
from app.db.sql.base_entity import (
    BaseEntity,
    type_updated_at,
)

"""
● Nombre total d’emprunts
● Nombre d’emprunts par semaine
● Auteur le plus emprunté
● Livre le plus emprunté
"""


class DashboardEntity(BaseEntity):
    __tablename__ = "admin_dashboard"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=guid_gen(16))
    total_loans: Mapped[int] = mapped_column(default=0)
    most_loaned_book: Mapped[str] = mapped_column(JSON, nullable=True)
    most_loaned_author: Mapped[str] = mapped_column(JSON, nullable=True)

    updated_at: Mapped[type_updated_at]

    def __repr__(self) -> str:
        return f"<DashboardEntity(id={self.id}, total_loans={self.total_loans}, most_loaned_book={self.most_loaned_book}, most_loaned_author={self.most_loaned_author})>"


class DashboardWeeklyEntity(BaseEntity):
    __tablename__ = "admin_weekly_dashboard"
    __table_args__ = (UniqueConstraint("week", "year", name="unique_week_year"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=guid_gen(16))
    week: Mapped[int] = mapped_column(default=0)
    year: Mapped[int] = mapped_column(default=0)
    total_loans: Mapped[int] = mapped_column(default=0)
    most_loaned_book: Mapped[str] = mapped_column(JSON, nullable=True)
    most_loaned_author: Mapped[str] = mapped_column(JSON, nullable=True)
    returned_loans: Mapped[int] = mapped_column(default=0)
    overdue_loans: Mapped[int] = mapped_column(default=0)

    updated_at: Mapped[type_updated_at]

    def __repr__(self) -> str:
        return f"<DashboardWeeklyEntity(id={self.id}, week={self.week}, year={self.year}, total_loans={self.total_loans})>"
