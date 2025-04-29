import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.sql.base_engine import get_session, base_engine
from app.db.guid import guid16
from .base_entity import BaseEntity
from app.auth.utils import pwd_context


import logging

logger = logging.getLogger("liboo.app.db.sql.init_db")


def cleanup(session: Session):
    # Clear existing data
    session.execute(text("DELETE FROM loans"))
    session.execute(text("DELETE FROM books"))
    session.execute(text("DELETE FROM users"))
    session.commit()


def _init_users(session: Session):
    # 1. Insert Users
    base_password = pwd_context.hash("chat123d")
    users_sql = f"""
    INSERT INTO users (id, username, password, role, email, address, max_week_loans) VALUES
    ('FpTP69ymJ4UyevD6', 'admin', '{base_password}', 'admin', 'admin@liboo.com', '123 Admin St', 3),
    ('C9QT05IKWXSDSIyd', 'librarian', '{base_password}', 'librarian', 'libr@liboo.com', '456 Librarian Ave', 3),
    ('fSlCc4K0hnGcf9Rr', 'loaner1', '{base_password}', 'loaner', 'user1@chat3d.com', '789 Loaner St', 3),
    ('Al6coTKH_11kM4bj', 'loaner2', '{base_password}', 'loaner', 'user2@chat3d.com', '789 Loaner St', 3),
    ('J_acuZFpxoGC7gLY', 'loaner3', '{base_password}', 'loaner', 'user3@chat3d.com', '789 Loaner St', 3)
    """
    session.execute(text(users_sql))
    session.commit()


def _init_authors(session: Session):
    # 1. Insert Authors
    authors_sql = """
    INSERT INTO authors (id, name, bio, created_by, updated_by) VALUES
    ('hwNQ0pjK9IvaaPi6', 'J.K. Rowling', 'British author, best known for the Harry Potter series.', 'FpTP69ymJ4UyevD6', 'FpTP69ymJ4UyevD6'),
    ('mUIGbHzQRUhCjH7x', 'George Orwell', 'English novelist and essayist, known for 1984 and Animal Farm.', 'FpTP69ymJ4UyevD6', 'FpTP69ymJ4UyevD6'),
    ('f9aMPS5CLDuSg6mv', 'Agatha Christie', 'Famous for her detective novels, particularly those featuring Hercule Poirot.', 'FpTP69ymJ4UyevD6', 'FpTP69ymJ4UyevD6'),
    ('YlaEPV9KZS_mqaK4', 'Stephen King', 'American author of horror, supernatural fiction, suspense, and fantasy novels.', 'FpTP69ymJ4UyevD6', 'FpTP69ymJ4UyevD6'),
    ('HAiG_0776d4qadS2', 'J.R.R. Tolkien', 'Best known for The Hobbit and The Lord of the Rings.', 'FpTP69ymJ4UyevD6', 'FpTP69ymJ4UyevD6'),
    ('bas6qGv4u36srk2P', 'Jane Austen', 'Known for her novels about the British landed gentry at the end of the 18th century.', 'FpTP69ymJ4UyevD6', 'FpTP69ymJ4UyevD6')
    """
    session.execute(text(authors_sql))
    session.commit()
    # 1. Insert Author


def _init_books(session: Session):
    # 2. Insert 20 Books
    authors = [
        "hwNQ0pjK9IvaaPi6",
        "mUIGbHzQRUhCjH7x",
        "f9aMPS5CLDuSg6mv",
        "YlaEPV9KZS_mqaK4",
        "HAiG_0776d4qadS2",
        "bas6qGv4u36srk2P",
    ]
    books_sql = "INSERT INTO books (id, title, author_id, isbn, status, note, year, description, created_by, updated_by) VALUES "
    book_values = []

    for i in range(1, 21):
        book_values.append(f"""(
            '{guid16()}',
            'Book {i}', 
            '{random.choice(authors)}', 
            '978{random.randint(100000000, 999999999)}', 
            'available',
            {random.randint(1, 5)}.0,
            {random.randint(1900, 2023)},
            'This is a description for Book {i}.',
            'FpTP69ymJ4UyevD6',
            'FpTP69ymJ4UyevD6'
        )""")

    session.execute(text(books_sql + ", ".join(book_values)))
    session.commit()


def _init_loans(session: Session):
    # 3. Insert 30 Loans over last 5 weeks
    loans_sql = "INSERT INTO loans (id, user_id, book_id, created_at, due, returned_at, status, created_by, updated_by) VALUES "
    loan_values = []
    today = datetime.utcnow()

    # Get user and book IDs
    users = session.execute(
        text("SELECT id FROM users WHERE role = 'loaner'")
    ).fetchall()
    books = session.execute(text("SELECT id FROM books")).fetchall()

    for i in range(30):
        loan_date = today - timedelta(days=random.randint(1, 35))  # Last 5 weeks
        due_date = loan_date + timedelta(days=7)
        returned = (
            loan_date + timedelta(days=random.randint(1, 7))
            if random.random() > 0.1
            else None
        )
        status = "active"
        if returned and returned > due_date:
            status = "late"
        elif returned and returned > loan_date:
            status = "returned"
        elif random.random() < 0.1:
            status = "lost"
        user_id = random.choice(users)[0]
        loan_values.append(f"""(
            '{guid16()}',
            '{user_id}', 
            '{random.choice(books)[0]}', 
            '{loan_date.isoformat()}', 
            '{due_date.isoformat()}', 
            {"NULL" if returned is None else f"'{returned.isoformat()}'"},
            '{status}',
            '{user_id}', 
            '{user_id}'
        )""")

    session.execute(text(loans_sql + ", ".join(loan_values)))
    session.commit()


def _init_dashboards(session: Session):
    # 4. Insert Dashboards
    loan_stats = session.execute(
        text("""
        SELECT 
            COUNT(*) as total_loans,
            (SELECT book_id FROM loans GROUP BY book_id ORDER BY COUNT(*) DESC LIMIT 1) as most_loaned_book,
            (SELECT author_id FROM loans 
             JOIN books ON loans.book_id = books.id 
             GROUP BY author_id ORDER BY COUNT(*) DESC LIMIT 1) as most_loaned_author
        FROM loans
        """)
    ).fetchone()

    # Insert dashboard data
    dashboards_sql = """
    INSERT INTO admin_dashboard (id, total_loans, most_loaned_book, most_loaned_author) 
    VALUES (:id, :total_loans, :most_loaned_book, :most_loaned_author)
    """
    most_loaned_book = session.execute(
        text("SELECT id, title, author_id, description FROM books WHERE id = :book_id"),
        {"book_id": loan_stats.most_loaned_book},
    ).fetchone()
    most_loaned_author = session.execute(
        text("SELECT id, name, bio FROM authors WHERE id = :author_id"),
        {"author_id": loan_stats.most_loaned_author},
    ).fetchone()
    session.execute(
        text(dashboards_sql),
        {
            "id": "admin_dashboard",
            "total_loans": loan_stats.total_loans,
            "most_loaned_book": json.dumps(most_loaned_book._asdict()),
            "most_loaned_author": json.dumps(most_loaned_author._asdict()),
        },
    )
    session.commit()


def __init_weekly_dashboards(session: Session):
    # 5. Insert Weekly Dashboards
    week_years = session.execute(
        text("""
        SELECT DISTINCT 
            strftime('%W', created_at) as week, 
            strftime('%Y', created_at) as year 
        FROM loans
        """)
    ).fetchall()

    for week, year in week_years:
        # Get weekly statistics in a single query
        stats = session.execute(
            text("""
            WITH weekly_loans AS (
                SELECT 
                    book_id,
                    user_id,
                    status
                FROM loans
                WHERE strftime('%W', created_at) = :week 
                AND strftime('%Y', created_at) = :year
            )
            SELECT
                COUNT(*) as total_loans,
                (SELECT book_id FROM weekly_loans 
                 GROUP BY book_id ORDER BY COUNT(*) DESC LIMIT 1) as most_loaned_book,
                (SELECT author_id FROM weekly_loans 
                 JOIN books ON weekly_loans.book_id = books.id 
                 GROUP BY author_id ORDER BY COUNT(*) DESC LIMIT 1) as most_loaned_author,
                SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as overdue_loans,
                SUM(CASE WHEN status = 'returned' THEN 1 ELSE 0 END) as returned_loans
            FROM weekly_loans
            """),
            {"week": week, "year": year},
        ).fetchone()
        most_loaned_book = session.execute(
            text(
                "SELECT id, title, author_id, description FROM books WHERE id = :book_id"
            ),
            {"book_id": stats.most_loaned_book},
        ).fetchone()
        most_loaned_author = session.execute(
            text("SELECT id, name, bio FROM authors WHERE id = :author_id"),
            {"author_id": stats.most_loaned_author},
        ).fetchone()

        # Insert weekly dashboard with proper parameter binding
        session.execute(
            text("""
            INSERT INTO admin_weekly_dashboard 
                (id, week, year, total_loans, most_loaned_book, most_loaned_author, overdue_loans, returned_loans) 
            VALUES 
                (:id, :week, :year, :total_loans, :most_loaned_book, :most_loaned_author, :overdue_loans, :returned_loans)
            """),
            {
                "id": f"weekly_dashboard_{week}_{year}",
                "week": week,
                "year": year,
                "total_loans": stats.total_loans or 0,
                "most_loaned_book": json.dumps(most_loaned_book._asdict()),
                "most_loaned_author": json.dumps(most_loaned_author._asdict()),
                "overdue_loans": stats.overdue_loans or 0,
                "returned_loans": stats.returned_loans or 0,
            },
        )

    session.commit()


def init_db(create_db: bool = True, session: Session = None):
    if create_db:
        BaseEntity.metadata.create_all(bind=base_engine)

    try:
        session = next(get_session()) if session is None else session
        # cleanup(session)
        # Check if data already exists in the "users" table; if so, skip further initialization.
        existing_data = session.execute(text("SELECT 1 FROM users LIMIT 1")).fetchone()
        if existing_data is not None:
            logger.info("Database already initialized. Skipping data insertion.")
            return
        _init_users(session)
        _init_authors(session)
        _init_books(session)
        _init_loans(session)
        _init_dashboards(session)
        __init_weekly_dashboards(session)

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        session.rollback()
        raise e
