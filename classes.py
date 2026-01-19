import pandas as pd
import sqlite3
from datetime import datetime

class ExpenseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """
        Initializes the table with a Primary Key.
        BEST PRACTICE: Always use an ID column for reliable row referencing.
        """
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Category TEXT,
                    Description TEXT,
                    Amount REAL
                )
            """)

    def load_data(self):
        """Loads data including the ID, but keeps it hidden in UI later."""
        with self.get_connection() as conn:
            try:
                df = pd.read_sql("SELECT * FROM expenses", conn, parse_dates=["Date"])
                return df
            except Exception:
                return pd.DataFrame(columns=["id", "Date", "Category", "Description", "Amount"])

    # IN FILE: classes.py -> Inside ExpenseManager class

    def save_bulk_data(self, df):
        with self.get_connection() as conn:
            with conn: # <--- CRITICAL: Starts a transaction block
                conn.execute("DELETE FROM expenses") 
                df.to_sql("expenses", conn, if_exists="append", index=False)

    def add_expense(self, category, description, amount):
        """Inserts the expense AND updates the budget balance in one transaction."""
        with self.get_connection() as conn:
            # 1. Record the Transaction
            conn.execute(
                "INSERT INTO expenses (Date, Category, Description, Amount) VALUES (?, ?, ?, ?)",
                (datetime.now(), category, description, amount)
            )         
            # 2. Deduct from the Budget Bucket
            conn.execute(
                "UPDATE budgets SET current_balance = current_balance - ? WHERE category = ?",
                (amount, category)
            )
            
        return self.load_data()

    @staticmethod # Static methods don't need self to work
    def calculate_metrics(df):
        if df.empty:
            return 0, 0
        return df["Amount"].sum(), len(df)
    
    @staticmethod
    def get_expenses_by_category(df):
        if df.empty:
            return pd.Series()
        return df.groupby("Category")["Amount"].sum()
    
    @staticmethod
    def get_category_matrix(df, categories):
        data_dict = {}
        max_len = 0
        
        for cat in categories:
            amounts = df[df["Category"] == cat]["Amount"].tolist()
            data_dict[cat] = amounts
            max_len = max(max_len, len(amounts))
            
        for cat in data_dict:
            data_dict[cat] += [None] * (max_len - len(data_dict[cat]))
            
        return pd.DataFrame(data_dict)


class BudgetManager:
    def __init__(self, db_path, allocation_map):
        self.db_path = db_path
        self.allocation_map = allocation_map # Now using percentages
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    category TEXT PRIMARY KEY,
                    current_balance REAL DEFAULT 0
                )
            """)
            # Ensure all categories in config exist in DB
            for cat in self.allocation_map.keys():
                conn.execute(
                    "INSERT OR IGNORE INTO budgets (category, current_balance) VALUES (?, 0)",
                    (cat,)
                )

    def get_balances(self):
        with self.get_connection() as conn:
            rows = conn.execute("SELECT category, current_balance FROM budgets").fetchall()
            return dict(rows)

    def allocate_income(self, income_amount):
        """
        Distributes income based on fixed percentages.
        """
        allocations = {}
        
        # Validation: Warn if config doesn't sum to 1.0 (Optional but recommended)
        total_pct = sum(self.allocation_map.values())
        if not (0.99 <= total_pct <= 1.01):
            print(f"WARNING: Allocation percentages sum to {total_pct}, not 1.0")

        with self.get_connection() as conn:
            for category, pct in self.allocation_map.items():
                if pct == 0:
                    continue
                    
                added_amount = income_amount * pct
                allocations[category] = added_amount
                
                conn.execute(
                    "UPDATE budgets SET current_balance = current_balance + ? WHERE category = ?",
                    (added_amount, category)
                )
        
        return allocations