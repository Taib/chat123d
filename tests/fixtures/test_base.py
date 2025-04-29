from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # Import StaticPool for SQLite in-memory

# Ensure all model modules are imported BEFORE BaseEntity.metadata is used.
# These imports register the models with BaseEntity's metadata.
import app.users.entities.entity
import app.authors.entities
import app.books.entities
import app.loans.entities
import app.admin_dashboard.entities

# Fixiing bug: Import BaseEntity AFTER potential model imports if BaseEntity is defined elsewhere,
from app.db.sql.base_entity import BaseEntity
from app.db.get_db import get_db
import app.db.sql.init_db as init_db
from app.app import app  # Import the actual FastAPI instance

# Use the SQLite in-memory database for testing
# Use StaticPool for in-memory DB to ensure the same connection is used
# check_same_thread=False is needed because pytest might use different threads
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Use StaticPool for :memory: db
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BaseEntity.metadata.create_all(bind=engine)

init_db_session = TestingSessionLocal()
try:
    init_db.init_db(create_db=False, session=init_db_session)
except Exception as e:
    init_db_session.rollback()
    print(f"Error during init_db: {e}")
    raise e
finally:
    init_db_session.close()


# Dependency override to use testing database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Ensure 'app' is the FastAPI instance
if isinstance(app, FastAPI):
    app.dependency_overrides[get_db] = override_get_db
else:
    raise TypeError(f"Expected 'app' to be a FastAPI instance, but got {type(app)}")

client = TestClient(app)


@pytest.fixture(
    scope="session"
)  # Changed scope to session as DB setup is once per session
def test_client():
    yield client


# Fixture for direct database access (function scope for isolation)
@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
