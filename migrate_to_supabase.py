import tomllib
from supabase import create_client

with open(".streamlit/secrets.toml", "rb") as file:
    secrets = tomllib.load(file)

supabase = create_client(
    secrets["SUPABASE_URL"],
    secrets["SUPABASE_KEY"]
)

tables = [
    "users",
    "clubs",
    "expenses",
    "memberships",
    "budgets",
    "club_budgets",
    "club_expenses",
    "programmes",
    "programme_participants"
]

print("Supabase record verification:")

total = 0

for table in tables:
    response = supabase.table(table).select(
        "id", count="exact"
    ).execute()

    count = response.count
    total += count

    print(f"{table}: {count} records")

print(f"\nTotal records: {total}")