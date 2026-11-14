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

def join_club(invitation_code, user_id):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Find the club using its invitation code
        cursor.execute("""
            SELECT id
            FROM clubs
            WHERE invitation_code = ?
        """, (invitation_code.strip().upper(),))

        club = cursor.fetchone()

        # Check whether the invitation code exists
        if club is None:
            return "invalid"

        club_id = club[0]

        # Add the user as a club member
        cursor.execute("""
            INSERT INTO memberships (user_id, club_id, role)
            VALUES (?, ?, ?)
        """, (user_id, club_id, "Member"))

        conn.commit()
        return "success"

    except sqlite3.IntegrityError:
        return "already_joined"

    finally:
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
def get_user_club_role(user_id, club_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role
        FROM memberships
        WHERE user_id = ? AND club_id = ?
    """, (user_id, club_id))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return None
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

def add_club_budget(club_id, category, budget_limit):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO club_budgets (club_id, category, budget_limit)
            VALUES (?, ?, ?)
        """, (club_id, category, budget_limit))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()

def get_club_budgets(club_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, category, budget_limit
        FROM club_budgets
        WHERE club_id = ?
    """, (club_id,))

    budgets = cursor.fetchall()

    conn.close()

    return budgets

def update_club_budget(club_id, category, new_budget_limit):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE club_budgets
        SET budget_limit = ?
        WHERE club_id = ? AND category = ?
    """, (new_budget_limit, club_id, category))

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated

def delete_club_budget(club_id, category):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM club_budgets
        WHERE club_id = ? AND category = ?
    """, (club_id, category))

    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()

    return deleted

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS club_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            club_id INTEGER NOT NULL,
            submitted_by INTEGER NOT NULL,
            expense_name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            receipt_path TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (club_id) REFERENCES clubs(id),
            FOREIGN KEY (submitted_by) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS club_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            club_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            budget_limit REAL NOT NULL,

            FOREIGN KEY (club_id) REFERENCES clubs(id),
            UNIQUE (club_id, category)
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
def get_total_club_budget(club_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(budget_limit)
        FROM club_budgets
        WHERE club_id = ?
    """, (club_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result[0] is not None else 0
def get_total_club_expenses(club_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM club_expenses
        WHERE club_id = ?
          AND status = 'Approved'
    """, (club_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result[0] is not None else 0
def get_category_expense_totals(club_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM club_expenses
        WHERE club_id = ?
          AND status = 'Approved'
        GROUP BY category
    """, (club_id,))

    expenses = cursor.fetchall()
    conn.close()

    return expenses

def get_remaining_club_budget(club_id):
    total_budget = get_total_club_budget(club_id) or 0
    total_expenses = get_total_club_expenses(club_id) or 0

    remaining = total_budget - total_expenses

    return remaining
def add_club_expense(club_id, user_id, expense_name, amount, category, receipt_path):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO club_expenses
        (club_id, submitted_by, expense_name, amount, category, receipt_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (club_id, user_id, expense_name, amount, category, receipt_path))

    conn.commit()
    conn.close()
def get_club_expenses(club_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, expense_name, amount, category,
               submitted_by, receipt_path, status, created_at
        FROM club_expenses
        WHERE club_id = ?
        ORDER BY created_at DESC
    """, (club_id,))

    expenses = cursor.fetchall()

    conn.close()

    return expenses
def get_username(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username
        FROM users
        WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return "Unknown User"
def update_expense_status(expense_id, club_id, user_id, status):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT role
            FROM memberships
            WHERE user_id = ? AND club_id = ?
        """, (user_id, club_id))

        result = cursor.fetchone()

        if result is None or result[0] != "Treasurer":
            return False

        if status not in ["Approved", "Rejected"]:
            return False

        cursor.execute("""
            UPDATE club_expenses
            SET status = ?
            WHERE id = ? AND club_id = ? AND status = 'Pending'
        """, (status, expense_id, club_id))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()
if __name__ == "__main__":
    create_table()
    print("Database and expense table created successfully!")
    
