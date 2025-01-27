import sqlite3
import MetaTrader5 as mt5
from flask import Flask, render_template
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

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
        closing_balance REAL,
        opened DATETIME
    )
    ''')

    conn.commit()
    conn.close()

def get_journal_data():
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journal')
    data = cursor.fetchall()
    conn.close()
    return data

def update_journal(account, name, opening_balance, gain, profit, closing_balance, opened):
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE journal SET name = ?, opening_balance = ?, gain = ?, profit = ?, closing_balance = ?, opened = ?
    WHERE account = ?
    ''', (name, opening_balance, gain, profit, closing_balance, opened, account))

    conn.commit()
    conn.close()

# Connect to MetaTrader 4 terminal
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# Connect to your trading account using environment variables
login = int(os.getenv('MT5_LOGIN'))
password = os.getenv('MT5_PASSWORD')
server = os.getenv('MT5_SERVER')

if not mt5.login(login, password=password, server=server):
    print("login() failed")
    mt5.shutdown()

def fetch_trade_data():
    # Fetch the latest trade data from MT5
    trades = mt5.positions_get()
    if trades:
        # Assuming only one user and one account for simplicity
        account = 1
        name = 'Tebogo'
        opening_balance = 10000.00  # Static value for now
        # Calculate gain, profit, and closing balance dynamically
        gain = 0.15  # Placeholder value
        profit = opening_balance + (gain * 100) # Placeholder value
        closing_balance = opening_balance + profit
        opened = datetime.now()  # Current date and time

        update_journal(account, name, opening_balance, gain, profit, closing_balance, opened)

@app.route('/')
def home():
    fetch_trade_data()
    data = get_journal_data()
    return render_template('journal.html', data=data)

if __name__ == '__main__':
    create_database()
    app.run(debug=True)
