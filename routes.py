from flask import render_template, jsonify, request
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
    return render_template('add_types.html')
