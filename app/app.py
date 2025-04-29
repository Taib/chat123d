from fastapi import FastAPI
import logging

from app.auth.controller import auth_router
from app.books.controller import books_router
from app.loans.controller import loans_router
from app.users.controllers import users_router
from app.admin_dashboard.controller import dashboard_router
from app.authors.controller import authors_router


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("liboo")
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)


def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    """
    # Initialize database connection
    from app.db.sql.init_db import init_db

    init_db()
    yield


app = FastAPI(
    title="Liboo API",
    description="Library Books API for basic Library Management",
    version="0.1.0",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Operations with authentication",
        },
        {
            "name": "books",
            "description": "Operations with books",
        },
        {
            "name": "authors",
            "description": "Operations with authors",
        },
        {
            "name": "users",
            "description": "Operations with users",
        },
        {
            "name": "loans",
            "description": "Operations with loans",
        },
        {
            "name": "dashboard",
            "description": "Operations with admin dashboard",
        },
    ],
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(books_router)
app.include_router(loans_router)
app.include_router(dashboard_router)
app.include_router(authors_router)
