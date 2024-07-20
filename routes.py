from flask import redirect, render_template, request
from main import app
import sqlite3


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/types")
def types():
    return render_template('types.html')

@app.route("/types/add", methods=["POST", "GET"])
def addtypes():
    if request.method == "POST":
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        name = request.form.get("name")
        cursor.execute("INSERT INTO type(name) values(?)", (name, ))
        conn.commit()
        conn.close()
        return redirect('/types')
    return render_template('add_types.html')

@app.route("/types/list")
def listtypes():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM type")
    types = cursor.fetchall()

    return render_template('list_types.html', types = types)
