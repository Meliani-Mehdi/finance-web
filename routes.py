from flask import redirect, render_template, request
from main import app
import sqlite3
import xlsxwriter
import plotly


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/types")
def types():
    return render_template('types.html')

@app.route("/types/add", methods=["POST", "GET"])
def addtypes():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template('err.html', message="Name is required")
        try:
            with sqlite3.connect('finance.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO type (name) VALUES (?)", (name,))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template('err.html', message="Type already exists")
        except Exception as e:
            return render_template('err.html', message=str(e))

        return redirect('/types')
    
    return render_template('add_types.html')

@app.route("/types/list")
def listtypes():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM type")
    types = cursor.fetchall()

    return render_template('list_types.html', types = types)

@app.route("/types/list/<int:id>")
def seetype(id):
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template('err.html', message="Name is required")
        try:
            with sqlite3.connect('finance.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO type (name) VALUES (?)", (name,))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template('err.html', message="Type already exists")
        except Exception as e:
            return render_template('err.html', message=str(e))

        return redirect('/types')
    
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM type WHERE id = ?", (id, ))
    name_val = cursor.fetchone()[0]
    return render_template('edit_types.html', val=name_val, id=id)

@app.route("/types/edit/<int:id>", methods=['POST'])
def edittype(id):
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template('err.html', message="Name is required")
        try:
            with sqlite3.connect('finance.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE type SET name = ? WHERE id = ?", (name,id))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template('err.html', message="Type already exists")
        except Exception as e:
            return render_template('err.html', message=str(e))
    return redirect("/types/list")

@app.route("/types/delete/<int:id>", methods=['POST'])
def deletetype(id):
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template('err.html', message="Name is required")
        try:
            with sqlite3.connect('finance.db') as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM type WHERE id = ?", (id, ))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template('err.html', message="Type already exists")
        except Exception as e:
            return render_template('err.html', message=str(e))
    return redirect("/types/list")

@app.route("/income")
def income():
    return render_template("income.html")

@app.route("/income/add", methods=["POST", "GET"])
def addincome():
    if request.method == "POST":
        pass
    return render_template("add_income.html")

@app.route("/expenses")
def expense():
    return render_template("expense.html")
