from typing import Any
from pydantic import BaseModel


class DashboardUpdate(BaseModel):
    total_loans: int | None = None
    most_loaned_book: str | None = None
    most_loaned_author: str | None = None
    # overdue_loans: int | None = None


class DashboardWeeklySave(BaseModel):
    week: int
    year: int
    total_loans: int | None = None
    most_loaned_book: str | None = None
    most_loaned_author: str | None = None
    overdue_loans: int | None = None
    returned_loans: int | None = None


class Dashboard(BaseModel):
    total_loans: int
    most_loaned_book: dict[str, Any] = {}
    most_loaned_author: dict[str, Any] = {}
    # overdue_loans: int


class DashboardWeekly(BaseModel):
    id: str
    week: int
    year: int
    total_loans: int
    most_loaned_book: dict[str, Any] = {}
    most_loaned_author: dict[str, Any] = {}
    overdue_loans: int
    returned_loans: int
