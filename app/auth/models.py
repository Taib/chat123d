from pydantic import BaseModel, EmailStr


class AuthRegister(BaseModel):
    username: str
    password: str
    address: str | None = None
    email: EmailStr | None = None


class TokenData(BaseModel):
    id: str
    role: str
    username: str
    email: str
    address: str
    max_week_loans: int


class AuthSession(BaseModel):
    access_token: str
    refresh_token: str
    user: TokenData
