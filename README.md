# Club Budget and Expense Tracker

A web-based financial management platform designed to help university clubs and societies manage budgets, track expenses, monitor financial activities, and manage programme deposits efficiently.

## Project Overview

The Club Budget and Expense Tracker aims to simplify financial management for university clubs by replacing manual spreadsheets and paper-based records with a centralized digital platform.

It allows club treasurers and committee members to manage financial activities, monitor spending, record transactions, and track programme payment collections in one place.

The platform helps improve financial transparency, organization, and accountability within university clubs.

## Live Website

[Club Budget and Expense Tracker](https://club-budget-and-expense-tracker.streamlit.app/)

## Key Features

- **Personal Finance:** Record and track personal expenses and manage category budgets.
- **Club Management:** Create clubs, join clubs, and manage member roles.
- **Club Budget Management:** Set, update, and monitor club budgets.
- **Expense Submission:** Submit expense requests with supporting receipts.
- **Expense Approval:** Allow treasurers to review, approve, or reject expense requests.
- **Expense History:** View and manage personal and club financial records.
- **Programme Deposit Management:** Create programmes, register participants, record payment status, and monitor deposit collections.
- **Receipt Management:** Upload and retrieve receipt files.
- **Financial Dashboard:** Monitor budgets, expenses, and remaining balances.

## Technologies Used

- **Python** – Main programming language.
- **Streamlit** – Web application framework.
- **Supabase (PostgreSQL)** – Cloud database for storing application data.
- **Supabase Storage** – Cloud storage for receipt files.
- **Pandas** – Data processing and table management.
- **Plotly** – Data visualization.
- **Bcrypt** – Password hashing.
- **GitHub** – Source code management and version control.
- **Streamlit Community Cloud** – Application deployment.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ngruqi0601-hub/Club-Budget-and-Expense-Tracker.git
```

### 2. Open the Project Folder

```bash
cd Club-Budget-and-Expense-Tracker
```

### 3. Install the Required Libraries

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase

Create a Supabase project and configure the database tables and Storage bucket required by the application.

Create a `.streamlit/secrets.toml` file in the project folder and add your own credentials:

```toml
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_secret_key"

[email]
sender = "your_email_address"
app_password = "your_email_app_password"
```

Replace the placeholder values with your own credentials.

**Important:** Never upload `secrets.toml` or expose your database credentials on GitHub. Add `.streamlit/secrets.toml` to `.gitignore`.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your web browser.

## Project Structure

```text
Club-Budget-and-Expense-Tracker/
│
├── app.py
├── database.py
├── navigation.py
├── storage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── pages/
│   ├── 0_Account.py
│   ├── 1_Finance_Selection.py
│   ├── 2_Expense_Entry.py
│   ├── 3_Expense_History.py
│   ├── 4_Budget_Setting.py
│   ├── 5_Club_Navigation.py
│   ├── 6_Club_Budget_Setting.py
│   ├── 7_Club_Expense_History.py
│   ├── 8_Club-Expense_Approval.py
│   ├── 9_Club_Expense_Submission.py
│   ├── 10_Personal_Dashboard.py
│   └── 11_programme_deposit.py
│
└── .streamlit/
    └── secrets.toml
```

## How to Use

1. Register a new account or log in.
2. Choose between Personal Finance and Club Finance.
3. Navigate to the desired feature.
4. Record personal expenses or manage club financial activities.
5. Set budgets and monitor spending.
6. Submit expense requests with supporting receipts.
7. Allow the treasurer to review and approve expense requests.
8. Manage programme registrations and track participant deposit payments.
9. Monitor financial records and budget summaries through the dashboard.

## Deployment

The application is deployed using Streamlit Community Cloud and connected to the GitHub repository.

The application uses Supabase as its cloud database, allowing financial records to persist independently of application deployments.

## Author

Developed as a university project.
## Author

**Name:** NG RU QI

**Project:** Club Budget and Expense Tracker

**Institution:** Universiti Teknologi Malaysia (UTM)