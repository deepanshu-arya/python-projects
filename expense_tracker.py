import sqlite3
from datetime import datetime

DB_NAME = "expenses.db"

# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Add a new expense
def add_expense(category, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
        (category, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    print("✅ Expense added successfully!")

# View all expenses
def view_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    print("\n📊 All Expenses:")
    print("-" * 40)
    for row in rows:
        print(f"ID: {row[0]} | Category: {row[1]} | Amount: ₹{row[2]} | Date: {row[3]}")
    print("-" * 40)

# Calculate total expenses
def total_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    conn.close()
    print(f"\n💰 Total Expenses: ₹{total if total else 0}")

# Main menu
def main():
    init_db()
    while True:
        print("\n====== Expense Tracker ======")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Total Expenses")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            category = input("Enter category (Food, Travel, Shopping, etc.): ")
            amount = float(input("Enter amount: "))
            add_expense(category, amount)

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            total_expenses()

        elif choice == "4":
            print("👋 Exiting... Have a great day!")
            break
        else:
            print("❌ Invalid choice, try again.")

if __name__ == "__main__":
    main()
