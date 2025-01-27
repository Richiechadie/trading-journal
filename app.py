import sqlite3
import MetaTrader5 as mt5
from flask import Flask, render_template
from dotenv import load_dotenv
import os
from datetime import datetime
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize debugger (optional)
# import debugpy
# debugpy.listen(('0.0.0.0', 5678))
# debugpy.wait_for_client()

def create_database():
    """Create the SQLite database and journal table if it doesn't exist."""
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
        closing_balance REAL,
        opened DATETIME
    )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database and table created successfully.")

def get_journal_data():
    """Fetch all data from the journal table."""
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journal')
    data = cursor.fetchall()
    conn.close()
    return data

def update_journal(account, name, opening_balance, gain, profit, closing_balance, opened):
    """
    Insert or update account data in the journal table.
    """
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    
    # Use INSERT OR REPLACE to handle updates
    cursor.execute('''
    INSERT OR REPLACE INTO journal (account, name, opening_balance, gain, profit, closing_balance, opened)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (account, name, opening_balance, gain, profit, closing_balance, opened))

    conn.commit()
    conn.close()
    logger.info(f"Journal updated for account {account}.")

def fetch_account_data():
    """
    Fetch account data from MT5 and insert it into the journal table.
    """
    # Connect to MetaTrader 5 terminal
    if not mt5.initialize():
        logger.error("Failed to initialize MT5 connection. Shutting down.")
        mt5.shutdown()
        return

    logger.info("MT5 initialized successfully.")

    # Connect to your trading account using environment variables
    login = int(os.getenv('MT5_LOGIN'))
    password = os.getenv('MT5_PASSWORD')
    server = os.getenv('MT5_SERVER')

    if not mt5.login(login, password=password, server=server):
        logger.error("Failed to log in to MT5 account. Shutting down.")
        mt5.shutdown()
        return

    logger.info("Logged in to MT5 account successfully.")

    # Fetch account information
    account_info = mt5.account_info()
    if account_info is None:
        logger.error("Failed to fetch account info.")
        mt5.shutdown()
        return

    logger.info(f"Account Info: {account_info}")

    # Prepare data for the journal
    account = account_info.login
    name = "Tebogo"  # Replace with actual name if available
    opening_balance = account_info.balance
    gain = (account_info.profit/account_info.balance * 100) 
    profit = account_info.profit
    closing_balance = account_info.equity
    opened = datetime.now()

    # Update the journal with the fetched data
    update_journal(account, name, opening_balance, gain, profit, closing_balance, opened)

    # Shutdown MT5 connection
    mt5.shutdown()
    logger.info("MT5 connection closed.")

@app.route('/')
def home():
    """Render the home page with journal data."""
    fetch_account_data()  # Fetch and update account data
    data = get_journal_data()  # Fetch data from the database
    return render_template('journal.html', data=data)

if __name__ == '__main__':
    create_database()  # Ensure the database and table exist
    app.run(debug=True)  # Run the Flask app