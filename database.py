import bcrypt
import secrets
import smtplib
import streamlit as st
from email.message import EmailMessage
from supabase import create_client


# =========================================================
# SUPABASE CONNECTION
# =========================================================

def get_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


def _is_unique_violation(error):
    return getattr(error, "code", None) == "23505"


def _as_tuples(rows, columns):
    """Convert Supabase dictionaries to the tuple format used by existing pages."""
    return [tuple(row.get(column) for column in columns) for row in rows]


# =========================================================
# GENERAL HELPERS
# =========================================================

def generate_invitation_code():
    return secrets.token_hex(4).upper()


# =========================================================
# CLUB CREATION AND MEMBERSHIP
# =========================================================

def create_club(club_name, user_id):
    supabase = get_supabase_client()
    invitation_code = generate_invitation_code()

    try:
        club_response = supabase.table("clubs").insert({
            "club_name": club_name,
            "invitation_code": invitation_code,
            "created_by": user_id
        }).select("id").execute()

        club_id = club_response.data[0]["id"]

        try:
            supabase.table("memberships").insert({
                "user_id": user_id,
                "club_id": club_id,
                "role": "Treasurer"
            }).execute()
        except Exception:
            # Avoid leaving a club without its creator membership.
            supabase.table("clubs").delete().eq("id", club_id).execute()
            raise

        return club_id, invitation_code

    except Exception as e:
        st.error(f"Unable to create club: {e}")
        return None, None


def join_club(invitation_code, user_id):
    supabase = get_supabase_client()

    try:
        response = supabase.table("clubs").select(
            "id"
        ).eq(
            "invitation_code", invitation_code.strip().upper()
        ).limit(1).execute()

        if not response.data:
            return "invalid"

        club_id = response.data[0]["id"]

        supabase.table("memberships").insert({
            "user_id": user_id,
            "club_id": club_id,
            "role": "Member"
        }).execute()

        return "success"

    except Exception as e:
        if _is_unique_violation(e):
            return "already_joined"
        st.error(f"Unable to join club: {e}")
        return "error"


def get_user_clubs(user_id):
    supabase = get_supabase_client()

    memberships = supabase.table("memberships").select(
        "club_id, role"
    ).eq("user_id", user_id).execute().data

    if not memberships:
        return []

    club_ids = [item["club_id"] for item in memberships]

    club_rows = supabase.table("clubs").select(
        "id, club_name"
    ).in_("id", club_ids).execute().data

    club_names = {item["id"]: item["club_name"] for item in club_rows}

    return [
        (item["club_id"], club_names[item["club_id"]], item["role"])
        for item in memberships
        if item["club_id"] in club_names
    ]


def get_user_club_role(user_id, club_id):
    response = get_supabase_client().table("memberships").select(
        "role"
    ).eq(
        "user_id", user_id
    ).eq(
        "club_id", club_id
    ).limit(1).execute()

    return response.data[0]["role"] if response.data else None


# =========================================================
# USER REGISTRATION AND LOGIN
# =========================================================

def register_user(username, email, password):
    supabase = get_supabase_client()

    username = username.strip()
    email = email.strip().lower()

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        supabase.table("users").insert({
            "username": username,
            "email": email,
            "password_hash": password_hash
        }).execute()

        return True

    except Exception as e:
        if _is_unique_violation(e):
            return False

        st.error(f"Registration failed: {e}")
        return False


def login_user(username, password):
    try:
        username = username.strip()

        response = get_supabase_client().table("users").select(
            "password_hash"
        ).eq("username", username).limit(1).execute()

        if not response.data:
            return False

        stored_hash = response.data[0]["password_hash"]

        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash
        )

    except Exception as e:
        st.error(f"Login failed: {e}")
        return False


# =========================================================
# CLUB DASHBOARD TOTALS
# =========================================================

def get_total_club_budget(club_id):
    rows = get_supabase_client().table("club_budgets").select(
        "budget_limit"
    ).eq("club_id", club_id).execute().data

    return sum(float(row["budget_limit"] or 0) for row in rows)


def get_total_club_expenses(club_id):
    rows = get_supabase_client().table("club_expenses").select(
        "amount"
    ).eq(
        "club_id", club_id
    ).eq(
        "status", "Approved"
    ).execute().data

    return sum(float(row["amount"] or 0) for row in rows)


def get_category_expense_totals(club_id):
    rows = get_supabase_client().table("club_expenses").select(
        "category, amount"
    ).eq(
        "club_id", club_id
    ).eq(
        "status", "Approved"
    ).execute().data

    totals = {}
    for row in rows:
        category = row["category"]
        totals[category] = totals.get(category, 0) + float(row["amount"] or 0)

    return [(category, amount) for category, amount in totals.items()]


def get_remaining_club_budget(club_id):
    return get_total_club_budget(club_id) - get_total_club_expenses(club_id)


# =========================================================
# CLUB EXPENSES
# =========================================================

def add_club_expense(
    club_id,
    user_id,
    expense_name,
    amount,
    category,
    receipt_path,
    description=None
):
    get_supabase_client().table("club_expenses").insert({
        "club_id": club_id,
        "submitted_by": user_id,
        "expense_name": expense_name,
        "amount": amount,
        "category": category,
        "receipt_path": receipt_path,
        "description": description,
        "status": "Pending"
    }).execute()


def get_club_expenses(club_id):
    supabase = get_supabase_client()

    expenses = supabase.table("club_expenses").select(
        "id, expense_name, amount, category, submitted_by, receipt_path, "
        "status, created_at, description, treasurer_remarks"
    ).eq(
        "club_id", club_id
    ).order(
        "created_at", desc=True
    ).execute().data

    if not expenses:
        return []

    user_ids = list({row["submitted_by"] for row in expenses})
    users = supabase.table("users").select(
        "id, username"
    ).in_("id", user_ids).execute().data

    usernames = {row["id"]: row["username"] for row in users}

    # Preserve the original 10-column tuple order expected by the pages.
    return [
        (
            row["id"],
            row["expense_name"],
            row["amount"],
            row["category"],
            usernames.get(row["submitted_by"], "Unknown User"),
            row["receipt_path"],
            row["status"],
            row["created_at"],
            row["description"],
            row["treasurer_remarks"]
        )
        for row in expenses
    ]


def get_username(user_id):
    try:
        if user_id is None:
            return "Unknown"

        supabase = get_supabase_client()

        response = (
            supabase.table("users")
            .select("username")
            .eq("id", int(user_id))
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]["username"]

        return "Unknown"

    except Exception as e:
        print(f"Error getting username: {e}")
        return "Unknown"

def update_expense_status(
    expense_id,
    club_id,
    user_id,
    status,
    treasurer_remarks=None
):
    if status not in ["Approved", "Rejected"]:
        return False

    supabase = get_supabase_client()

    membership = supabase.table("memberships").select(
        "role"
    ).eq(
        "user_id", user_id
    ).eq(
        "club_id", club_id
    ).limit(1).execute().data

    if not membership or membership[0]["role"] != "Treasurer":
        return False

    response = supabase.table("club_expenses").update({
        "status": status,
        "treasurer_remarks": treasurer_remarks
    }).eq(
        "id", expense_id
    ).eq(
        "club_id", club_id
    ).eq(
        "status", "Pending"
    ).select("id").execute()

    return bool(response.data)


def get_user_id(username):
    response = get_supabase_client().table("users").select(
        "id"
    ).eq("username", username).limit(1).execute()

    return response.data[0]["id"] if response.data else None


# =========================================================
# CLUB BUDGETS
# =========================================================

def add_club_budget(club_id, category, budget_limit):
    try:
        get_supabase_client().table("club_budgets").insert({
            "club_id": club_id,
            "category": category,
            "budget_limit": budget_limit
        }).execute()
        return True
    except Exception as e:
        if _is_unique_violation(e):
            return False
        st.error(f"Unable to add club budget: {e}")
        return False


def get_club_budgets(club_id):
    rows = get_supabase_client().table("club_budgets").select(
        "id, category, budget_limit"
    ).eq("club_id", club_id).execute().data

    return _as_tuples(rows, ["id", "category", "budget_limit"])


def update_club_budget(club_id, category, new_budget_limit):
    response = get_supabase_client().table("club_budgets").update({
        "budget_limit": new_budget_limit
    }).eq(
        "club_id", club_id
    ).eq(
        "category", category
    ).select("id").execute()

    return bool(response.data)


def delete_club_budget(club_id, category):
    response = get_supabase_client().table("club_budgets").delete().eq(
        "club_id", club_id
    ).eq(
        "category", category
    ).select("id").execute()

    return bool(response.data)


# =========================================================
# PASSWORD RESET
# =========================================================

def check_account_exists(username, email):
    username = username.strip()
    email = email.strip().lower()

    response = get_supabase_client().table("users").select(
        "id"
    ).eq(
        "username", username
    ).eq(
        "email", email
    ).limit(1).execute()

    return bool(response.data)


def reset_password(username, email, new_password):
    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    response = get_supabase_client().table("users").update({
        "password_hash": password_hash
    }).eq(
        "username", username
    ).eq(
        "email", email
    ).select("id").execute()

    return bool(response.data)


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


# =========================================================
# PERSONAL FINANCE
# =========================================================

def add_expense(user_id, expense_name, amount, category):
    get_supabase_client().table("expenses").insert({
        "user_id": user_id,
        "expense_name": expense_name,
        "amount": amount,
        "category": category
    }).execute()


def add_budget(user_id, category, budget_limit):
    get_supabase_client().table("budgets").insert({
        "user_id": user_id,
        "category": category,
        "budget_limit": budget_limit
    }).execute()


def update_budget(user_id, category, budget_limit):
    get_supabase_client().table("budgets").update({
        "budget_limit": budget_limit
    }).eq(
        "user_id", user_id
    ).eq(
        "category", category
    ).execute()


def delete_budget(user_id, category):
    get_supabase_client().table("budgets").delete().eq(
        "user_id", user_id
    ).eq(
        "category", category
    ).execute()


def get_budgets(user_id):
    rows = get_supabase_client().table("budgets").select(
        "id, user_id, category, budget_limit"
    ).eq("user_id", user_id).execute().data

    # Match the old SQLite SELECT * column order.
    return _as_tuples(rows, ["id", "user_id", "category", "budget_limit"])


def get_expenses(user_id):
    rows = get_supabase_client().table("expenses").select(
        "id, expense_name, amount, category, user_id"
    ).eq("user_id", user_id).execute().data

    # Match the old SQLite SELECT * column order.
    return _as_tuples(rows, ["id", "expense_name", "amount", "category", "user_id"])


def delete_expense(expense_id, user_id):
    get_supabase_client().table("expenses").delete().eq(
        "id", expense_id
    ).eq(
        "user_id", user_id
    ).execute()


def migrate_personal_data(user_id):
    """
    Kept for compatibility with any old page imports.
    Personal records are already assigned to user_id in Supabase,
    so no schema migration is needed here.
    """
    return True


# =========================================================
# PROGRAMMES AND DEPOSIT MANAGEMENT
# =========================================================

def add_programme(club_id, programme_name, deposit_amount, participant_limit):
    try:
        response = get_supabase_client().table("programmes").insert({
            "club_id": club_id,
            "programme_name": programme_name,
            "deposit_amount": deposit_amount,
            "participant_limit": participant_limit
        }).execute()

        return bool(response.data)

    except Exception as e:
        print(f"Error creating programme: {e}")
        return False


def get_programmes(club_id):
    rows = get_supabase_client().table("programmes").select(
        "id, programme_name, deposit_amount, created_at, participant_limit"
    ).eq(
        "club_id", club_id
    ).order(
        "created_at", desc=True
    ).execute().data

    return _as_tuples(
        rows,
        ["id", "programme_name", "deposit_amount", "created_at", "participant_limit"]
    )


def add_programme_participant(programme_id, participant_name, participant_email):
    get_supabase_client().table("programme_participants").insert({
        "programme_id": programme_id,
        "participant_name": participant_name,
        "participant_email": participant_email
    }).execute()


def get_programme_participants(programme_id):
    rows = get_supabase_client().table("programme_participants").select(
        "id, participant_name, participant_email, payment_status, "
        "payment_proof, registered_at"
    ).eq(
        "programme_id", programme_id
    ).order(
        "registered_at", desc=True
    ).execute().data

    return _as_tuples(
        rows,
        [
            "id",
            "participant_name",
            "participant_email",
            "payment_status",
            "payment_proof",
            "registered_at"
        ]
    )


def update_participant_payment_status(participant_id, programme_id, payment_status):
    response = get_supabase_client().table("programme_participants").update({
        "payment_status": payment_status
    }).eq(
        "id", participant_id
    ).eq(
        "programme_id", programme_id
    ).select("id").execute()

    return bool(response.data)


def update_participant_payment_proof(participant_id, programme_id, payment_proof):
    response = get_supabase_client().table("programme_participants").update({
        "payment_proof": payment_proof
    }).eq(
        "id", participant_id
    ).eq(
        "programme_id", programme_id
    ).select("id").execute()

    return bool(response.data)


def update_programme(programme_id, deposit_amount, participant_limit):
    response = get_supabase_client().table("programmes").update({
        "deposit_amount": deposit_amount,
        "participant_limit": participant_limit
    }).eq(
        "id", programme_id
    ).select("id").execute()

    return bool(response.data)


def update_participant_details(
    participant_id,
    programme_id,
    participant_name,
    participant_email
):
    response = get_supabase_client().table("programme_participants").update({
        "participant_name": participant_name,
        "participant_email": participant_email
    }).eq(
        "id", participant_id
    ).eq(
        "programme_id", programme_id
    ).select("id").execute()

    return bool(response.data)


def delete_participant_payment_proof(participant_id, programme_id):
    response = get_supabase_client().table("programme_participants").update({
        "payment_proof": None
    }).eq(
        "id", participant_id
    ).eq(
        "programme_id", programme_id
    ).select("id").execute()

    return bool(response.data)


# =========================================================
# LEGACY SQLITE SETUP COMPATIBILITY
# =========================================================

def create_connection():
    raise RuntimeError(
        "SQLite is no longer used. This project now connects to Supabase."
    )


def update_club_expenses_table():
    # Supabase schema has already been created.
    return True


def create_table():
    # Supabase schema has already been created.
    return True


def create_programmes_table():
    # Supabase schema has already been created.
    return True


def create_participants_table():
    # Supabase schema has already been created.
    return True


if __name__ == "__main__":
    print("This application uses Supabase PostgreSQL.")
