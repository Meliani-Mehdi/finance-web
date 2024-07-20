from flask import Flask
import sqlite3
import xlsxwriter
import plotly
import webview
app = Flask(__name__)
from routes import *

def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            info TEXT,
            FOREIGN KEY (type) REFERENCES type(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            info TEXT,
            FOREIGN KEY (type) REFERENCES type(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS type (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL 
        )
    ''')
    
    conn.close()

init_db()


if __name__ == '__main__':
    app.run(debug=True)
