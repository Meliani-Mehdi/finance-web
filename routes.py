from flask import redirect, render_template, request
from main import app
import os
import sqlite3
import xlsxwriter
import plotly
import datetime


def fetch_data(table_name, time_period):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    if time_period == "all":
        query = f"SELECT * FROM {table_name}"
        params = ()
    else:
        now = datetime.datetime.now()
        if time_period == "day":
            start_date = now.strftime("%Y-%m-%d")
            end_date = start_date
        elif time_period == "week":
            start_date = (now - datetime.timedelta(days=now.weekday())).strftime(
                "%Y-%m-%d"
            )
            end_date = now.strftime("%Y-%m-%d")
        elif time_period == "month":
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        elif time_period == "year":
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        else:
            conn.close()
            return None

        query = f"SELECT * FROM {table_name} WHERE date BETWEEN ? AND ?"
        params = (start_date, end_date)

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


@app.route("/")
def index():
    return render_template("index.html")


# types


@app.route("/types")
def types():
    return render_template("types.html")


@app.route("/types/add", methods=["POST", "GET"])
def addtypes():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("err.html", message="Name is required")
        try:
            with sqlite3.connect("finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO type (name) VALUES (?)", (name,))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template("err.html", message="Type already exists")
        except Exception as e:
            return render_template("err.html", message=str(e))

        return redirect("/types")

    return render_template("add_types.html")


@app.route("/types/list")
def listtypes():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM type")
    types = cursor.fetchall()

    return render_template("list_types.html", types=types)


@app.route("/types/list/<int:id>")
def seetype(id):
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("err.html", message="Name is required")
        try:
            with sqlite3.connect("finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO type (name) VALUES (?)", (name,))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template("err.html", message="Type already exists")
        except Exception as e:
            return render_template("err.html", message=str(e))

        return redirect("/types")

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM type WHERE id = ?", (id,))
    name_val = cursor.fetchone()[0]
    return render_template("edit_types.html", val=name_val, id=id)


@app.route("/types/edit/<int:id>", methods=["POST"])
def edittype(id):
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("err.html", message="Name is required")
        try:
            with sqlite3.connect("finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE type SET name = ? WHERE id = ?", (name, id))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template("err.html", message="Type already exists")
        except Exception as e:
            return render_template("err.html", message=str(e))
    return redirect("/types/list")


@app.route("/types/delete/<int:id>", methods=["POST"])
def deletetype(id):
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("err.html", message="Name is required")
        try:
            with sqlite3.connect("finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM type WHERE id = ?", (id,))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template("err.html", message="Type already exists")
        except Exception as e:
            return render_template("err.html", message=str(e))
    return redirect("/types/list")


# income


@app.route("/income")
def income():
    return render_template("income.html")


@app.route("/income/sheet")
def income_sheet():
    return render_template("income_t.html")


@app.route("/income/add", methods=["POST", "GET"])
def addincome():
    if request.method == "POST":
        pass
    return render_template("add_income.html")


@app.route("/income/sheet/<time>")
def income_sheet_time(time):
    return render_template("expense_t.html")


# expense


@app.route("/expenses")
def expense():
    return render_template("expense.html")


@app.route("/expenses/sheet")
def expense_sheet():
    return render_template("expense_t.html")


@app.route("/expenses/sheet/<time>")
def expense_sheet_time(time):
    return render_template("expense_t.html")


@app.route("/close")
def close_app():
    os._exit(0)
