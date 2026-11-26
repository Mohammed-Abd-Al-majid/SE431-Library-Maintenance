
"""SQLite queries separated from business logic."""

import sqlite3
from .constraints import DEFAULT_BOOK_COPIES


def connect(path="library.db"):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def setup(connection):
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                available INTEGER NOT NULL DEFAULT 1
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT NOT NULL,
                book_id INTEGER NOT NULL,
                borrow_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                returned INTEGER NOT NULL DEFAULT 0
            )
        """)


def seed_demo_data(connection):
    """Insert example records without overwriting existing ones."""
    with connection:
        connection.executemany(
            "INSERT OR IGNORE INTO members VALUES (?, ?, ?)",
            [
                ("M001", "Sample Member", "ACTIVE"),
                ("M002", "Inactive Member", "INACTIVE"),
            ],
        )

        connection.executemany(
            "INSERT OR IGNORE INTO books VALUES (?, ?, ?, ?)",
            [
                (1, "Python Basics", "A. Writer",
                 DEFAULT_BOOK_COPIES),
                (2, "Database Design", "B. Writer",
                 DEFAULT_BOOK_COPIES),
            ],
        )


def get_member(connection, member_id):
    return connection.execute(
        "SELECT * FROM members WHERE id = ?",
        (member_id,)
    ).fetchone()


def count_active_loans(connection, member_id):
    return connection.execute(
        """SELECT COUNT(*) FROM loans
           WHERE member_id = ? AND returned = 0""",
        (member_id,)
    ).fetchone()[0]


def get_book(connection, book_id):
    return connection.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()


def decrease_availability(connection, book_id):
    result = connection.execute(
        """UPDATE books
           SET available = available - 1
           WHERE id = ? AND available > 0""",
        (book_id,)
    )
    return result.rowcount == 1


def create_loan(
    connection, member_id, book_id, borrowed_on, due_on
):
    connection.execute(
        """INSERT INTO loans
           (member_id, book_id, borrow_date, due_date, returned)
           VALUES (?, ?, ?, ?, 0)""",
        (
            member_id,
            book_id,
            borrowed_on.isoformat(),
            due_on.isoformat(),
        ),
    )


def get_active_loan(connection, member_id, book_id):
    return connection.execute(
        """SELECT * FROM loans
           WHERE member_id = ?
           AND book_id = ?
           AND returned = 0
           ORDER BY id DESC LIMIT 1""",
        (member_id, book_id),
    ).fetchone()


def close_loan(connection, loan_id):
    connection.execute(
        """UPDATE loans SET returned = 1
           WHERE id = ? AND returned = 0""",
        (loan_id,),
    )


def increase_availability(connection, book_id):
    connection.execute(
        """UPDATE books
           SET available = available + 1
           WHERE id = ?""",
        (book_id,),
    )


def find_books(connection, keyword):
    return connection.execute(
        """SELECT * FROM books
           WHERE title LIKE ? OR author LIKE ?
           ORDER BY id""",
        (f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
