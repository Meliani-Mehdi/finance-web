from flask import redirect, render_template, request, send_file
from datetime import datetime, timedelta
from main import app
import os
import sqlite3
import xlsxwriter
import plotly


def fetch_data(table_name, time_period):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    if time_period == "all":
        query = f"SELECT * FROM {table_name}"
        params = ()
    else:
        now = datetime.now()
        if time_period == "day":
            start_date = now.strftime("%Y-%m-%d")
            end_date = start_date
        elif time_period == "week":
            start_date = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
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
        date = datetime.now().strftime("%Y-%m-%d")
        t_type = request.form.get("type")
        amount = request.form.get("amount")
        info = request.form.get("comment")
        try:
            with sqlite3.connect("finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO income(date, type, amount, info) VALUES(?, ?, ?, ?)",
                    (date, t_type, amount, info),
                )
                conn.commit()

        except sqlite3.IntegrityError:
            return render_template(
                "err.html",
                message=f"Integrity Was Not Respected {date} {t_type} {amount} {info}",
            )
        except Exception as e:
            return render_template("err.html", message=str(e))
        return redirect("/income")
    try:
        with sqlite3.connect("finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM type")
            data = cursor.fetchall()
    except Exception as e:
        return render_template("err.html", message=str(e))
    return render_template("add_income.html", types=data)


@app.route("/income/sheet/<time>")
def income_sheet_time(time):
    data = fetch_data("income", time)

    file_name = f"income_sheet_{time}.xlsx"
    file_path = os.path.join("sheets", file_name)

    if not os.path.exists("sheets"):
        os.makedirs("sheets")

    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet("Income Sheet")

    header_format = workbook.add_format(
        {"bold": True, "bg_color": "#D7E4BC", "border": 1}
    )
    currency_format = workbook.add_format({"num_format": "$#,##0.00", "border": 1})
    date_format = workbook.add_format({"num_format": "yyyy-mm-dd", "border": 1})
    total_format = workbook.add_format(
        {"bold": True, "bg_color": "#FFEB9C", "border": 1}
    )

    headers = ["ID", "Date", "Type", "Amount", "Info"]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, header_format)

    for row_num, row_data in enumerate(data, start=1):
        worksheet.write(row_num, 0, row_data[0])  # ID
        worksheet.write(row_num, 1, row_data[1], date_format)  # Date
        worksheet.write(row_num, 2, row_data[2])  # Type
        worksheet.write(row_num, 3, row_data[3], currency_format)  # Amount
        worksheet.write(row_num, 4, row_data[4])  # Info

    total_row = len(data) + 1
    worksheet.write(total_row, 2, "Total", total_format)
    worksheet.write_formula(total_row, 3, f"=SUM(D2:D{total_row})", total_format)

    worksheet.set_column(0, 0, 5)  # ID
    worksheet.set_column(1, 1, 15)  # Date
    worksheet.set_column(2, 2, 15)  # Type
    worksheet.set_column(3, 3, 15)  # Amount
    worksheet.set_column(4, 4, 30)  # Info

    workbook.close()

    return render_template("err.html", message="Done")


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
