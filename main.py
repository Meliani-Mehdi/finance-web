from flask import Flask
import sqlite3
import xlsxwriter
import plotly
app = Flask(__name__)
from routes import *

def init_db():
    pass


if __name__ == '__main__':
    app.run(debug=True)
