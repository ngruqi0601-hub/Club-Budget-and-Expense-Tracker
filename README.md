# Club Budget and Expense Tracker

A web-based financial management platform designed to help university clubs and societies manage budgets, track expenses, monitor financial activities, and manage programme deposits efficiently.

## Project Overview

The Club Budget and Expense Tracker aims to simplify financial management for university clubs by replacing manual spreadsheets and paper-based records with a centralized digital platform.

It allows club treasurers and committee members to manage financial activities, monitor spending, record transactions, and track programme payment collections in one place.

The platform helps improve financial transparency, organization, and accountability within university clubs.
## Key Features

- **Personal Finance:** Record and track personal expenses.
- **Club Budget Management:** Set and monitor club budgets.
- **Expense Submission:** Submit expenses for approval.
- **Expense Approval:** Review and approve expense requests.
- **Expense History:** View and manage financial records.
- **Programme Deposit Management:** Manage participant registrations and payment status.
## Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- GitHub
## Installation and Setup

1. Clone the repository:

   ```bash
   git clone <your-repository-link>
   ```

2. Open the project folder:

   ```bash
   cd Club-Budget-and-Expense-Tracker
   ```

3. Install the required libraries:

   ```bash
   pip install streamlit pandas
   ```

4. Run the application:

   ```bash
   streamlit run app.py
   ```
## Project Structure

```text
Club-Budget-and-Expense-Tracker/
│
├── app.py
├── database.py
├── navigation.py
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
│   └── 11_programme_deposit.py
│
└── README.md
```
## How to Use

1. Register a new account or log in.
2. Choose between Personal Finance and Club Finance.
3. Navigate to the desired feature.
4. Record expenses, manage budgets, or submit expense requests.
5. Track financial records and monitor payment status.