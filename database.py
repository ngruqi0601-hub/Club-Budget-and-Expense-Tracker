import sqlite3
import bcrypt
import secrets
import smtplib
import streamlit as st
from email.message import EmailMessage
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
    return club_id, invitation_code

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
def register_user(username, email, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

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

        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

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
def add_club_expense(
    club_id,
    user_id,
    expense_name,
    amount,
    category,
    receipt_path,
    description=None
):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO club_expenses (
            club_id,
            submitted_by,
            expense_name,
            amount,
            category,
            receipt_path,
            description,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', CURRENT_TIMESTAMP)
    """, (
        club_id,
        user_id,
        expense_name,
        amount,
        category,
        receipt_path,
        description
    ))

    conn.commit()
    conn.close()
def get_club_expenses(club_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            club_expenses.id,
            club_expenses.expense_name,
            club_expenses.amount,
            club_expenses.category,
            users.username,
            club_expenses.receipt_path,
            club_expenses.status,
            club_expenses.created_at,
            club_expenses.description,
            club_expenses.treasurer_remarks
        FROM club_expenses
        JOIN users
        ON club_expenses.submitted_by = users.id
        WHERE club_expenses.club_id = ?
        ORDER BY club_expenses.created_at DESC
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
def update_expense_status(
    expense_id,
    club_id,
    user_id,
    status,
    treasurer_remarks=None
):
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
            SET status = ?, treasurer_remarks = ?
            WHERE id = ? AND club_id = ? AND status = 'Pending'
        """, (
            status,
            treasurer_remarks,
            expense_id,
            club_id
        ))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()
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
    
def update_club_expenses_table():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(club_expenses)")

    columns = [column[1] for column in cursor.fetchall()]

    if "description" not in columns:
        cursor.execute("""
            ALTER TABLE club_expenses
            ADD COLUMN description TEXT
        """)

    if "treasurer_remarks" not in columns:
        cursor.execute("""
            ALTER TABLE club_expenses
            ADD COLUMN treasurer_remarks TEXT
        """)

    conn.commit()
    conn.close()

    
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
            description TEXT,
            treasurer_remarks TEXT,

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

#reset password feature
def check_email_exists(email):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE email = ?
    """, (email,))

    result = cursor.fetchone()

    conn.close()

    return result is not None
def reset_password(email, new_password):
    conn = create_connection()
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE email = ?
    """, (password_hash, email))

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated
def send_verification_email(receiver_email, verification_code):

    message = EmailMessage()

    message["Subject"] = "Password Reset Verification Code"
    message["From"] = st.secrets["email"]["sender"]
    message["To"] = receiver_email

    message.set_content(f"""
Hello,

You requested to reset your password.

Your verification code is: {verification_code}

This code expires in 5 minutes.

If you did not request this, please ignore this email.

Thank you.
""")

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(
            st.secrets["email"]["sender"],
            st.secrets["email"]["app_password"]
            )
        server.send_message(message)





        


# ==============================
# PERSONAL FINANCE FUNCTIONS
# ==============================

def add_expense(user_id, expense_name, amount, category):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (user_id, expense_name, amount, category)
        VALUES (?, ?, ?, ?)
    """, (user_id, expense_name, amount, category))

    conn.commit()
    conn.close()


def add_budget(user_id, category, budget_limit):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budgets (user_id, category, budget_limit)
        VALUES (?, ?, ?)
    """, (user_id, category, budget_limit))

    conn.commit()
    conn.close()


def update_budget(user_id, category, budget_limit):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE budgets
        SET budget_limit = ?
        WHERE user_id = ? AND category = ?
    """, (budget_limit, user_id, category))

    conn.commit()
    conn.close()


def delete_budget(user_id, category):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM budgets
        WHERE user_id = ? AND category = ?
    """, (user_id, category))

    conn.commit()
    conn.close()


def get_budgets(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM budgets
        WHERE user_id = ?
    """, (user_id,))

    budgets = cursor.fetchall()
    conn.close()

    return budgets


def get_expenses(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        WHERE user_id = ?
    """, (user_id,))

    expenses = cursor.fetchall()
    conn.close()

    return expenses


def delete_expense(expense_id, user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM expenses
        WHERE id = ? AND user_id = ?
    """, (expense_id, user_id))

    conn.commit()
    conn.close()




def migrate_personal_data(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Check whether expenses already has a user_id column
        cursor.execute("PRAGMA table_info(expenses)")
        expense_columns = [column[1] for column in cursor.fetchall()]

        if "user_id" not in expense_columns:
            cursor.execute("""
                ALTER TABLE expenses
                ADD COLUMN user_id INTEGER REFERENCES users(id)
            """)

        # Check whether budgets already has a user_id column
        cursor.execute("PRAGMA table_info(budgets)")
        budget_columns = [column[1] for column in cursor.fetchall()]

        if "user_id" not in budget_columns:
            # Rebuild budgets to allow the same category
            # for different users
            cursor.execute("""
                ALTER TABLE budgets RENAME TO budgets_old
            """)

            cursor.execute("""
                CREATE TABLE budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category TEXT NOT NULL,
                    budget_limit REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, category)
                )
            """)

            cursor.execute("""
                INSERT INTO budgets (id, user_id, category, budget_limit)
                SELECT id, NULL, category, budget_limit
                FROM budgets_old
            """)

            cursor.execute("DROP TABLE budgets_old")

        # Assign existing personal records to this account
        cursor.execute("""
            UPDATE expenses
            SET user_id = ?
            WHERE user_id IS NULL
        """, (user_id,))

        cursor.execute("""
            UPDATE budgets
            SET user_id = ?
            WHERE user_id IS NULL
        """, (user_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        
#programme

def create_programmes_table():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            club_id INTEGER NOT NULL,
            programme_name TEXT NOT NULL,
            deposit_amount REAL NOT NULL,
            participant_limit integer NOT NULL DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (club_id) REFERENCES clubs(id)
        )
    """)

    conn.commit()
    conn.close()

def add_programme(
    club_id,
    programme_name,
    deposit_amount,
    participant_limit
):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO programmes (
            club_id,
            programme_name,
            deposit_amount,
            participant_limit
        )
        VALUES (?, ?, ?, ?)
    """, (
        club_id,
        programme_name,
        deposit_amount,
        participant_limit
    ))

    conn.commit()
    conn.close()


def get_programmes(club_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
       SELECT
       id,
       programme_name,
       deposit_amount,
       created_at,
       participant_limit,
       FROM programmes
       WHERE club_id = ?
       ORDER BY created_at DESC
    """, (club_id,))

    programmes = cursor.fetchall()

    conn.close()

    return programmes
def get_programmes(club_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            programme_name,
            deposit_amount,
            created_at,
            participant_limit
        FROM programmes
        WHERE club_id = ?
        ORDER BY created_at DESC
    """, (club_id,))

    programmes = cursor.fetchall()

    conn.close()

    return programmes

def create_participants_table():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programme_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programme_id INTEGER NOT NULL,
            participant_name TEXT NOT NULL,
            participant_email TEXT,
            payment_status TEXT NOT NULL DEFAULT 'Unpaid',
            payment_proof TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (programme_id) REFERENCES programmes(id)
        )
    """)

    conn.commit()
    conn.close()

def add_programme_participant(
    programme_id,
    participant_name,
    participant_email
):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO programme_participants (
            programme_id,
            participant_name,
            participant_email
        )
        VALUES (?, ?, ?)
    """, (
        programme_id,
        participant_name,
        participant_email
    ))

    conn.commit()
    conn.close()

def get_programme_participants(programme_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            participant_name,
            participant_email,
            payment_status,
            payment_proof,
            registered_at
        FROM programme_participants
        WHERE programme_id = ?
        ORDER BY registered_at DESC
    """, (programme_id,))

    participants = cursor.fetchall()

    conn.close()

    return participants
def update_participant_payment_status(
    participant_id,
    programme_id,
    payment_status
):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE programme_participants
        SET payment_status = ?
        WHERE id = ? AND programme_id = ?
    """, (payment_status, participant_id, programme_id))

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated
def update_participant_payment_proof(
    participant_id,
    programme_id,
    payment_proof
):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE programme_participants
        SET payment_proof = ?
        WHERE id = ? AND programme_id = ?
    """, (payment_proof, participant_id, programme_id))

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated
def update_programme(programme_id, deposit_amount, participant_limit):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE programmes
        SET deposit_amount = ?,
            participant_limit = ?
        WHERE id = ?
    """, (deposit_amount, participant_limit, programme_id))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated
def update_participant_details(participant_id, programme_id, participant_name, participant_email):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE programme_participants
        SET participant_name = ?,
            participant_email = ?
        WHERE id = ? AND programme_id = ?
    """, (
        participant_name,
        participant_email,
        participant_id,
        programme_id
    ))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated
def delete_participant_payment_proof(
    participant_id,
    programme_id
):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE programme_participants
        SET payment_proof = NULL
        WHERE id = ? AND programme_id = ?
    """, (participant_id, programme_id))

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated
if __name__ == "__main__":
    create_table()
    update_club_expenses_table()
    create_programmes_table()
    create_participants_table()
    print("Database and expense table created successfully!")
    
