from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.constants import AppConfig

SQL_DB_URL = AppConfig().pg_dsn or  "sqlite+pysqlite:///:memory:"

base_engine = create_engine(SQL_DB_URL, echo=False)

base_session = sessionmaker(bind=base_engine)


def get_session() -> Generator[Session, None, None]:
    """
    Yields a new session object.
    """

    session = base_session()
    yield session
    session.close()
