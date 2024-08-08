from flask import Flask
import sqlite3
import webview
from screeninfo import get_monitors
import keyboard

app = Flask(__name__)
from routes import *


def init_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            info TEXT,
            FOREIGN KEY (type) REFERENCES type(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            info TEXT,
            FOREIGN KEY (type) REFERENCES type(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS type (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL 
        )
    """)

    conn.close()


init_db()


if __name__ == "__main__":
    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    window = webview.create_window(
        "finance",
        app,
        width=screen_width,
        height=screen_height,
        resizable=True,
    )

    def toggle_fullscreen():
        window.toggle_fullscreen()

    keyboard.add_hotkey("F11", toggle_fullscreen)

    webview.start()
