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

    def save_bulk_data(self, df):
        """
        Safely updates the database without dropping the table.
        Strategy: Truncate (Delete all) -> Append. 
        This preserves the Table Schema (Primary Keys, constraints).
        """
        with self.get_connection() as conn:
            conn.execute("DELETE FROM expenses") 
            df.to_sql("expenses", conn, if_exists="append", index=False)

    def add_expense(self, category, description, amount):
        """Inserts a single row letting SQL handle the Timestamp and ID."""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO expenses (Date, Category, Description, Amount) VALUES (?, ?, ?, ?)",
                (datetime.now(), category, description, amount)
            )
        return self.load_data()

    def calculate_metrics(self, df):
        if df.empty:
            return 0, 0
        return df["Amount"].sum(), len(df)
    
    def get_expenses_by_category(self, df):
        if df.empty:
            return pd.Series()
        return df.groupby("Category")["Amount"].sum()
    
    def get_category_matrix(self, df, categories):
        data_dict = {}
        max_len = 0
        
        for cat in categories:
            amounts = df[df["Category"] == cat]["Amount"].tolist()
            data_dict[cat] = amounts
            max_len = max(max_len, len(amounts))
            
        # Pad lists
        for cat in data_dict:
            data_dict[cat] += [None] * (max_len - len(data_dict[cat]))
            
        return pd.DataFrame(data_dict)