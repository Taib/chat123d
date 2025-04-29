import datetime
from pydantic import BaseModel, EmailStr


class UserNewBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    address: str


class UserNewLender(UserNewBase):
    pass


class UserNewLibrarian(UserNewBase):
    pass


class UserNew(UserNewBase):
    role: str = "lender"
    max_week_loans: int = 3


class UserUpdate(BaseModel):
    id: str
    username: str | None = None
    email: str | None = None
    password: str | None = None
    address: str | None = None
    max_week_loans: int | None = None
    role: str | None = None


class User(BaseModel):
    id: str
    username: str
    email: str
    address: str
    max_week_loans: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    role: str
    loans: list[dict] | None = None  # noqa: F821


class UserWithPassword(User):
    password: str
