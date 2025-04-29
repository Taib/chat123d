from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.loans.entities import LoanEntity
from app.db.sql.base_repository import BaseRepository
from app.db.sql.utils import pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from app.loans.models import (
    Loan,
    LoanCreate,
    LoanUpdateDue,
    LoanUpdateReturn,
)
from app.auth.auth_guard import get_current_active_user
from app.db.get_db import get_db
from app.users.models.models import User
from app.books.repository import BookRepository
from app.users.repositories.inject_repo import get_users_repository
from app.users.repositories.repository import IUsersRepository
from app.constants import AppConfig
from app.books.models import BookUpdate


import logging

logger = logging.getLogger("liboo.app.loans.repository")


def loan_entity_to_model(entity: LoanEntity) -> Loan:
    """
    Convert a LoanEntity to a model.
    """
    return sqlalchemy_to_pydantic(entity, Loan, exclude={"password"})


def loan_model_to_entity(model: Loan) -> LoanEntity:
    """
    Convert a model to a LoanEntity.
    """
    return pydantic_to_sqlalchemy(model, LoanEntity, exclude_unset=True)


def get_week_start_date(date: datetime | None = None) -> datetime:
    """
    Return the start date of the week for the given date.
    If no date is provided, use today's date.
    """
    if date is None:
        date = datetime.today()
    return date - timedelta(
        days=date.weekday()
    )  # Fyi: Monday is the first day of the week


class LoanRepository(BaseRepository[LoanEntity]):
    def __init__(
        self,
        session: Session = Depends(get_db),
        user: User = Depends(get_current_active_user),
        users_repo: IUsersRepository = Depends(get_users_repository),
        books_repo: BookRepository = Depends(),
    ):
        super().__init__(
            LoanEntity,
            session,
        )
        self.user = user
        self.users_repo = users_repo
        self.books_repo = books_repo

    def get_loan(self, loan_id: str) -> Loan | None:
        """
        Get a loan by ID.
        """
        loan = self.find_by_id(loan_id)
        if loan:
            return loan_entity_to_model(loan)
        return None

    def get_all_loans(self) -> list[Loan]:
        """
        Get all loans.
        """
        loans = self.query().all()
        return [loan_entity_to_model(loan) for loan in loans]

    def get_user_loans(self, user_id: str = None) -> list[Loan]:
        """
        Get all user loans.
        """
        loans = (
            self.query()
            .filter_by(user_id=user_id if user_id is not None else self.user.id)
            .all()
        )
        return [loan_entity_to_model(loan) for loan in loans]

    def get_user_loans_overdue(self, user_id: str = None) -> list[Loan]:
        """
        Get all user loans overdue.
        """
        loans = (
            self.query()
            .filter(
                LoanEntity.user_id == user_id if user_id is not None else self.user.id,
                LoanEntity.due <= datetime.now(),
            )
            .all()
        )
        return [loan_entity_to_model(loan) for loan in loans]

    def get_user_week_loans(self, user_id: str = None) -> list[Loan]:
        """
        Get all user loans for the current week.
        """
        week_start = get_week_start_date()
        loans = (
            self.query()
            .filter(
                LoanEntity.id == user_id if user_id is not None else self.user.id,
                or_(
                    LoanEntity.created_at >= week_start,
                    LoanEntity.created_at < week_start + timedelta(days=7),
                ),
            )
            .all()
        )
        return [loan_entity_to_model(loan) for loan in loans]

    def get_active_loan_by_book_id(self, book_id: str) -> Loan | None:
        """
        Get an active loan by book ID.
        """
        loan = (
            self.query()
            .filter(
                LoanEntity.book_id == book_id,
                LoanEntity.status != "returned",
            )
            .first()
        )
        if loan:
            return loan_entity_to_model(loan)
        return None

    def create_loan(self, loan: LoanCreate) -> Loan:
        """
        Create a new loan.
        """

        try:
            entity = loan_model_to_entity(loan)
            entity.created_by = self.user.id
            entity.updated_by = self.user.id
            entity.due = datetime.now() + timedelta(days=AppConfig().loan_duration_days)
            result = self.create(entity)
            self.books_repo.update_book(BookUpdate(id=result.book_id, status="loaned"))
            return loan_entity_to_model(result)
        except Exception as e:
            logger.error(f"Error creating loan: {e}")
            raise ValueError("loan-creation-failed")

    def can_create(self, loan: LoanCreate) -> bool:
        """
        Check if a loan can be created.
        """

        book = self.books_repo.get_book(loan.book_id)
        if not book:
            raise ValueError("book-not-found")
        if book.status != "available":
            raise ValueError("book-not-available")
        user = (
            self.user
            if loan.user_id == self.user.id
            else self.users_repo.get_user(loan.user_id)
        )
        if not user:
            raise ValueError("user-not-found")
        week_loans = self.get_user_week_loans(user_id=user.id)
        if len(week_loans) >= user.max_week_loans:
            raise ValueError("user-loan-limit-reached")
        overdue_loans = self.get_user_loans_overdue(user_id=user.id)
        if len(overdue_loans) > AppConfig().max_overdue_loans:
            raise ValueError("too-many-overdue-loans")
        return True

    def update_loan(self, loan: LoanUpdateReturn | LoanUpdateDue) -> Loan:
        """
        Update an existing loan.
        """
        dump = loan.model_dump(exclude_unset=True)
        if loan.returned_at:
            dump["status"] = "returned"
        dump["updated_by"] = self.user.id
        self.update(loan.id, dump)
        updated_loan = self.find_by_id(loan.id)
        self.books_repo.update_book(
            BookUpdate(
                id=updated_loan.book_id,
                status="available" if updated_loan.status == "returned" else "loaned",
            )
        )
        return updated_loan

    def delete_loan(self, loan_id: str) -> bool:
        """
        Delete a loan by ID.
        """
        return self.delete(loan_id)
