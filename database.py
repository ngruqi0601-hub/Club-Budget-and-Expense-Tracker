import sqlite3
def create_connection():
    conn = sqlite3.connect("club_budget.db")
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

if __name__ == "__main__":
    create_table()
    print("Database and expense table created successfully!")
    
