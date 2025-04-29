from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.get_db import get_db
from app.users.repositories.sql_repository import SQLUsersRepository


# A way to support multiple databases in the future
def get_users_repository(
    database: Session = Depends(get_db),
) -> SQLUsersRepository:
    """
    Get the users repository.
    """
    if isinstance(database, Session):
        return SQLUsersRepository(database)
    raise ValueError("Only SQL database is supported.")
