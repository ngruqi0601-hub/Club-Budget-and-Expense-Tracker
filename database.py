import sqlite3
import bcrypt
import secrets
def generate_invitation_code():
    return secrets.token_hex(4).upper()
def create_club(club_name, user_id):
    conn = create_connection()
    cursor = conn.cursor()

    invitation_code = generate_invitation_code()

    cursor.execute("""
        INSERT INTO clubs (club_name, invitation_code, created_by)
        VALUES (?, ?, ?)
    """, (club_name, invitation_code, user_id))

    club_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO memberships (user_id, club_id, role)
        VALUES (?, ?, ?)
    """, (user_id, club_id, "Treasurer"))

    conn.commit()
    conn.close()

    return invitation_code
def get_user_clubs(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT clubs.id, clubs.club_name, memberships.role
        FROM memberships
        JOIN clubs ON memberships.club_id = clubs.id
        WHERE memberships.user_id = ?
    """, (user_id,))

    clubs = cursor.fetchall()
    conn.close()

    return clubs
def get_user_id(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None
def create_connection():
    conn = sqlite3.connect("club_budget.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE,
        budget_limit REAL NOT NULL
    )
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_name TEXT NOT NULL,
        invitation_code TEXT NOT NULL UNIQUE,
        created_by INTEGER NOT NULL,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        club_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (club_id) REFERENCES clubs(id),
        UNIQUE(user_id, club_id)
    )
""")
    conn.commit()
    conn.close()
def add_expense(expense_name, amount, category):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (expense_name, amount, category)
        VALUES (?, ?, ?)
    """, (expense_name, amount, category))

    conn.commit()
    conn.close()
def add_budget(category, budget_limit):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budgets (category, budget_limit)
        VALUES (?, ?)
    """, (category, budget_limit))

    conn.commit()
    conn.close()
def update_budget(category, budget_limit):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE budgets
        SET budget_limit = ?
        WHERE category = ?
    """, (budget_limit, category))

    conn.commit()
    conn.close()
def delete_budget(category):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM budgets WHERE category = ?",
        (category,)
    )

    conn.commit()
    conn.close()
def get_budgets():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM budgets")

    budgets = cursor.fetchall()

    conn.close()

    return budgets
def get_expenses():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")

    expenses = cursor.fetchall()

    conn.close()
    return expenses
def delete_expense(expense_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()
def register_user(username, email, password):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (username, email, password_hash))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()
def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        stored_hash = result[0]

        if bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash
        ):
            return True

    return False
if __name__ == "__main__":
    create_table()
    print("Database and expense table created successfully!")
    
