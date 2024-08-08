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
        query = f"""
                SELECT {table_name}.id, date, name, amount, info
                FROM {table_name}
                JOIN type ON {table_name}.type = type.id
            """
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

        query = f"""
            SELECT {table_name}.id, date, name, amount, info
            FROM {table_name}
            JOIN type ON {table_name}.type = type.id
            WHERE date BETWEEN ? AND ?
        """
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


@app.route("/income/sheet/<time>", methods=["POST", "GET"])
def income_sheet_time(time):
    data = fetch_data("income", time)
    if request.method == "POST":
        file_name = f"income_sheet_{time}.xlsx"
        file_path = os.path.join("sheets", file_name)

        if not os.path.exists("sheets"):
            os.makedirs("sheets")

        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet("Income Sheet")

        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#4F81BD",
                "font_color": "#FFFFFF",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        currency_format = workbook.add_format(
            {
                "num_format": "#,##0.00",
                "border": 1,
                "align": "right",
            }
        )
        date_format = workbook.add_format(
            {
                "num_format": "yyyy-mm-dd",
                "border": 1,
                "align": "center",
            }
        )
        total_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#FFC000",
                "border": 1,
                "align": "right",
            }
        )
        highlight_format = workbook.add_format(
            {
                "bg_color": "#C6EFCE",
                "font_color": "#006100",
            }
        )
        summary_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#DCE6F1",
                "border": 1,
                "align": "right",
            }
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

        worksheet.conditional_format(
            f"D2:D{len(data)+1}",
            {
                "type": "cell",
                "criteria": ">",
                "value": 1000,
                "format": highlight_format,
            },
        )

        total_row = len(data) + 1
        worksheet.write(total_row, 2, "Total", total_format)
        worksheet.write_formula(total_row, 3, f"=SUM(D2:D{total_row})", total_format)

        summary_row = total_row + 2
        worksheet.write(summary_row, 2, "Average", summary_format)
        worksheet.write_formula(
            summary_row, 3, f"=AVERAGE(D2:D{total_row})", summary_format
        )
        worksheet.write(summary_row + 1, 2, "Max", summary_format)
        worksheet.write_formula(
            summary_row + 1, 3, f"=MAX(D2:D{total_row})", summary_format
        )
        worksheet.write(summary_row + 2, 2, "Min", summary_format)
        worksheet.write_formula(
            summary_row + 2, 3, f"=MIN(D2:D{total_row})", summary_format
        )

        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 40)

        worksheet.freeze_panes(1, 0)

        worksheet.autofilter(0, 0, total_row - 1, len(headers) - 1)

        workbook.close()

        return render_template("err.html", message="Done")
    return render_template("income_sheet.html", datas=data)


# expense


@app.route("/expenses")
def expense():
    return render_template("expense.html")


@app.route("/expenses/sheet")
def expense_sheet():
    return render_template("expense_t.html")


@app.route("/expenses/sheet/<time>", methods=["POST", "GET"])
def expense_sheet_time(time):
    data = fetch_data("expenses", time)
    if request.method == "POST":
        file_name = f"expense_sheet_{time}.xlsx"
        file_path = os.path.join("sheets", file_name)

        if not os.path.exists("sheets"):
            os.makedirs("sheets")

        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet("Expense Sheet")

        # Define formats
        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#4F81BD",
                "font_color": "#FFFFFF",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        currency_format = workbook.add_format(
            {
                "num_format": "#,##0.00",
                "border": 1,
                "align": "right",
            }
        )
        date_format = workbook.add_format(
            {
                "num_format": "yyyy-mm-dd",
                "border": 1,
                "align": "center",
            }
        )
        total_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#FFC000",
                "border": 1,
                "align": "right",
            }
        )
        highlight_format = workbook.add_format(
            {
                "bg_color": "#FFC7CE",
                "font_color": "#9C0006",
            }
        )
        summary_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#DCE6F1",
                "border": 1,
                "align": "right",
            }
        )

        # Write headers
        headers = ["ID", "Date", "Type", "Amount", "Info"]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        # Write data rows
        for row_num, row_data in enumerate(data, start=1):
            worksheet.write(row_num, 0, row_data[0])  # ID
            worksheet.write(row_num, 1, row_data[1], date_format)  # Date
            worksheet.write(row_num, 2, row_data[2])  # Type
            worksheet.write(row_num, 3, row_data[3], currency_format)  # Amount
            worksheet.write(row_num, 4, row_data[4])  # Info

        # Apply conditional formatting for Amount > $1000
        worksheet.conditional_format(
            f"D2:D{len(data)+1}",
            {
                "type": "cell",
                "criteria": ">",
                "value": 1000,
                "format": highlight_format,
            },
        )

        # Calculate and write totals
        total_row = len(data) + 1
        worksheet.write(total_row, 2, "Total", total_format)
        worksheet.write_formula(total_row, 3, f"=SUM(D2:D{total_row})", total_format)

        # Summary section
        summary_row = total_row + 2
        worksheet.write(summary_row, 2, "Average", summary_format)
        worksheet.write_formula(
            summary_row, 3, f"=AVERAGE(D2:D{total_row})", summary_format
        )
        worksheet.write(summary_row + 1, 2, "Max", summary_format)
        worksheet.write_formula(
            summary_row + 1, 3, f"=MAX(D2:D{total_row})", summary_format
        )
        worksheet.write(summary_row + 2, 2, "Min", summary_format)
        worksheet.write_formula(
            summary_row + 2, 3, f"=MIN(D2:D{total_row})", summary_format
        )

        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 40)

        worksheet.freeze_panes(1, 0)

        worksheet.autofilter(0, 0, total_row - 1, len(headers) - 1)

        workbook.close()

        return render_template("err.html", message="Done")
    return render_template("expense_sheet.html", datas=data)


@app.route("/expenses/add", methods=["POST", "GET"])
def addexpense():
    if request.method == "POST":
        date = datetime.now().strftime("%Y-%m-%d")
        t_type = request.form.get("type")
        amount = request.form.get("amount")
        info = request.form.get("comment")
        try:
            with sqlite3.connect("finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO expenses(date, type, amount, info) VALUES(?, ?, ?, ?)",
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
        return redirect("/expenses")
    try:
        with sqlite3.connect("finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM type")
            data = cursor.fetchall()
    except Exception as e:
        return render_template("err.html", message=str(e))
    return render_template("add_expense.html", types=data)
