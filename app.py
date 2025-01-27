import sqlite3

def create_database():
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS journal (
        account INTEGER PRIMARY KEY,
        name TEXT,
        opening_balance REAL, 
        gain REAL,
        profit REAL,
        closing_balance REAL
    )
    ''')

    # Insert dummy data
    cursor.execute('''
    INSERT INTO journal (account, name, opening_balance, gain, profit, closing_balance)
    VALUES (1, 'Tebogo', 10000.00, 0.15, 1500.00, 11500.00)
    ''')

    conn.commit()
    conn.close()

# Call the function to create the database and insert dummy data
if __name__ == '__main__':
    create_database()
