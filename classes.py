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
