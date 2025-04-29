from pydantic import BaseModel


class AuthorCreate(BaseModel):
    name: str
    bio: str | None = None


class AuthorUpdate(BaseModel):
    id: str
    name: str | None = None
    bio: str | None = None


class Author(BaseModel):
    id: str
    name: str
    bio: str | None = None
