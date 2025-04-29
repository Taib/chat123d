from sqlalchemy.orm import Session
from app.db.sql.base_engine import get_session
from app.constants import AppConfig


def get_db() -> Session:
    """
    Get the database engine.

    A way to support multiple databases in the future
    """
    if AppConfig().db_type != "sql":
        raise ValueError("Only SQL database is supported.")
    return next(get_session())
