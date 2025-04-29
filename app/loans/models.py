import datetime
from typing import Literal
from pydantic import BaseModel


type LoanStatus = Literal["active", "returned", "lost", "late"]


class LoanCreate(BaseModel):
    user_id: str
    book_id: str


class LoanUpdateReturn(BaseModel):
    id: str
    returned_at: datetime.datetime | None = None


class LoanUpdateDue(BaseModel):
    id: str
    due: datetime.datetime | None = None


class Loan(BaseModel):
    id: str
    user_id: str
    book_id: str
    due: datetime.datetime
    returned_at: datetime.datetime | None = None
    status: LoanStatus = "active"
    book: dict | None = None
    user: dict | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    created_by: str
    updated_by: str
