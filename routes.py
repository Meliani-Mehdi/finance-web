from flask import render_template, jsonify, request
from main import app


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/types")
def types():
    return render_template('types.html')

@app.route("/types/add")
def addtypes():
    return render_template('add_types.html')
