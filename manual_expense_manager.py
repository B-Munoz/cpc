import pandas as pd
import os

class FinanceManager:
    def __init__(self, filename="expenses.csv"):
        self.filename = filename
        self.categories = ["Transporte", "Vivienda", "Misceláneo"]
        self.columns = ["Category", "Description", "Amount"]
        self.df = self.load_data()

    def load_data(self):
        """Loads existing CSV or creates an empty DataFrame."""
        if os.path.exists(self.filename):
            try:
                return pd.read_csv(self.filename)
            except pd.errors.EmptyDataError:
                pass
        return pd.DataFrame(columns=self.columns)

    def save_data(self):
        """Saves current data to CSV."""
        self.df.to_csv(self.filename, index=False)
        print(f"Data saved to {self.filename}")

    def get_valid_number(self, prompt):
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Error: Please enter a valid number.")

    def select_category(self):
        print("\nSelect a category:")
        for i, category in enumerate(self.categories, 1):
            print(f"{i}. {category}")
        
        while True:
            try:
                choice = int(input("Option number: "))
                if 1 <= choice <= len(self.categories):
                    return self.categories[choice - 1]
                print("Invalid option number.")
            except ValueError:
                print("Please enter a number.")

    def add_expense(self):
        while True:
            print("\n--- Add New Expense ---")
            amount = self.get_valid_number("Enter amount: ")
            description = input("Enter description: ").strip() or "No description"
            category = self.select_category()

            # Create a new record as a DataFrame
            new_row = pd.DataFrame([{
                "Category": category,
                "Description": description,
                "Amount": amount
            }])

            # Concatenate to the main DataFrame
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            print(f"Added: {category} - {description}: ${amount}")

            if input("Add another? (y/n): ").lower().strip() != 'y':
                break
        
        # Save after the batch of additions
        self.save_data()

    def show_summary(self):
        if self.df.empty:
            print("No expenses recorded.")
            return
        
        print("\n--- Expenses Summary ---")
        print(self.df)
        print("\nTotal by Category:")
        print(self.df.groupby("Category")["Amount"].sum())

def main():
    manager = FinanceManager()
    
    while True:
        print("\n1. Add Expense")
        print("2. Show Summary")
        print("3. Exit")
        choice = input("Choose an action: ")

        if choice == '1':
            manager.add_expense()
        elif choice == '2':
            manager.show_summary()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()